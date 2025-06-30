"""
CLI Plugin for Cisco-style IP Route Command
Author: Alperen Akpinar
Email: alperen.akpinar@nokia.com
"""
from srlinux.mgmt.cli import CliPlugin
from srlinux.syntax import Syntax
from srlinux.location import build_path
from srlinux.data import Border, TagValueFormatter
import datetime
import ipaddress

class Plugin(CliPlugin):
    """A Cisco-style IP route CLI plugin"""
    def load(self, cli, **_kwargs):
        # Add commands to show mode
        show_cmd = cli.show_mode

        # Create 'ip' command under show mode
        ip_cmd = show_cmd.add_command(
            Syntax('ip'),
            callback=None
        )

        # Create 'route' command under 'ip'
        route_cmd = ip_cmd.add_command(
            Syntax('route'),
            callback=self._show_ip_route
        )

        # Add VRF option
        route_cmd.add_command(
            Syntax('vrf')
            .add_unnamed_argument('vrf_name', suggestions=self._get_network_instances),
            callback=self._show_vrf_route
        )

    def _get_network_instances(self, state, *args, **kwargs):
        """Get list of configured network-instances for auto-completion"""
        try:
            ni_path = build_path('/network-instance[name=*]')
            ni_data = state.server_data_store.get_data(ni_path)
            instances = [ni.name for ni in ni_data.network_instance.items()]
            
            # Remove 'default' from suggestions as it's implied by the base command
            if 'default' in instances:
                instances.remove('default')
            
            # Check for partial word in kwargs
            partial_word = kwargs.get('partial_word', '')
            
            # If a partial word is provided, filter suggestions
            if partial_word:
                instances = [inst for inst in instances if inst.startswith(partial_word)]
            
            return instances
        except Exception as e:
            return []

    def _show_ip_route(self, state, output, **_kwargs):
        """Show routes for default network-instance"""
        self._show_routes(state, output, network_instance='default')

    def _show_vrf_route(self, state, output, arguments, **_kwargs):
        """Show routes for specified VRF"""
        network_instance = arguments.get('vrf_name')
        self._show_routes(state, output, network_instance=network_instance)

    def _format_uptime(self, route):
        """Extract and format uptime for a route"""
        try:
            if not getattr(route, 'active', False):
                return ""

            if route.route_type == 'bgp':
                try:
                    last_update_str = route.last_app_update
                    if last_update_str:
                        timestamp = last_update_str.split(' (')[0]
                        last_update_time = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        current_time = datetime.datetime.now(datetime.timezone.utc)
                        uptime = current_time - last_update_time
                        days, seconds = uptime.days, uptime.seconds
                        hours = seconds // 3600
                        if days > 0:
                            return f"{days}d{hours:02d}h"
                        else:
                            minutes, seconds = divmod(seconds % 3600, 60)
                            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                except Exception:
                    pass
            return ""
        except Exception:
            return ""

    def _show_routes(self, state, output, network_instance):
        print('''!!! Third-party Cisco-style CLI plugin. Output may differ from native SR Linux display.\n''')
        print('''Codes: C - connected, L - local, S - static, B - BGP, O - OSPF, IS - IS-IS,
       Ag - aggregate, Ar - arp-nd, BL - bgp-label, BE - bgp-evpn, BV - bgp-vpn
       D - dhcp, G - gribi, H - host, Li - linux, N1/N2 - ndk\n''')

        # Show which VRF we're displaying
        if network_instance != 'default':
            print(f'Routing Table: VRF {network_instance}\n')

        routes_path = build_path(f'/network-instance[name={network_instance}]/route-table/ipv4-unicast/route')
        try:
            routes_data = state.server_data_store.get_data(routes_path, recursive=True)
        except Exception:
            print(f"Error: VRF '{network_instance}' not found or no routes present.")
            print(f"\n-> Try 'show network-instance {network_instance} route-table' for the best insights.")
            return

        default_route_exists = False
        all_routes = []

        for ni in routes_data.network_instance.items():
            route_table = ni.route_table.get()
            ipv4_unicast = route_table.ipv4_unicast.get()

            for route in ipv4_unicast.route.items():
                if route.ipv4_prefix == '0.0.0.0/0':
                    default_route_exists = True

                route_type = route.route_type
                route_owner = route.route_owner
                ipv4_prefix = route.ipv4_prefix

                code = self._get_route_code(route_type, route_owner)

                route_entry = {
                    'prefix': ipv4_prefix,
                    'code': code,
                    'type': route_type,
                    'owner': route_owner,
                    'next_hops': [],
                    'uptime': self._format_uptime(route),
                    'interface': None,
                    'preference': route.preference,
                    'metric': route.metric
                }

                if route_type in ['local', 'connected'] and route_owner in ['local_mgr', 'net_inst_mgr']:
                    # Get interface from next-hop group
                    next_hop_group = getattr(route, 'next_hop_group', None)
                    if next_hop_group:
                        try:
                            nhg_path = build_path(f'/network-instance[name={network_instance}]/route-table/next-hop-group[index={next_hop_group}]')
                            nhg_data = state.server_data_store.get_data(nhg_path, recursive=True)
                            # Get subinterface from next-hop
                            for ni in nhg_data.network_instance.items():
                                nhg = ni.route_table.get().next_hop_group.get()
                                for nh in nhg.next_hop.items():
                                    if hasattr(nh, 'next_hop') and getattr(nh, 'resolved', False):
                                        nh_path = build_path(f'/network-instance[name={network_instance}]/route-table/next-hop[index={nh.next_hop}]')
                                        nh_data = state.server_data_store.get_data(nh_path, recursive=True)
                                        for route_nh in nh_data.network_instance.items():
                                            next_hop = route_nh.route_table.get().next_hop.get()
                                            subinterface = getattr(next_hop, 'subinterface', None)
                                            if subinterface:
                                                route_entry['interface'] = subinterface
                                                break
                        except Exception:
                            pass

                next_hop_group = getattr(route, 'next_hop_group', None)

                if next_hop_group:
                    try:
                        nhg_path = build_path(f'/network-instance[name={network_instance}]/route-table/next-hop-group[index={next_hop_group}]')
                        nhg_data = state.server_data_store.get_data(nhg_path, recursive=True)

                        next_hops = []
                        for ni in nhg_data.network_instance.items():
                            nhg = ni.route_table.get().next_hop_group.get()
                            for nh in nhg.next_hop.items():
                                if hasattr(nh, 'next_hop') and getattr(nh, 'resolved', False):
                                    nh_path = build_path(f'/network-instance[name={network_instance}]/route-table/next-hop[index={nh.next_hop}]')
                                    nh_data = state.server_data_store.get_data(nh_path, recursive=True)
                                    for route_nh in nh_data.network_instance.items():
                                        next_hop = route_nh.route_table.get().next_hop.get()
                                        ip_address = getattr(next_hop, 'ip_address', None)
                                        subinterface = getattr(next_hop, 'subinterface', None)
                                        
                                        if ip_address:
                                            next_hops.append({
                                                'ip': ip_address,
                                                'interface': subinterface or ''
                                            })

                        route_entry['next_hops'] = next_hops
                    except Exception:
                        pass

                all_routes.append(route_entry)

        if not default_route_exists:
            print("Gateway of last resort is not set")

        sorted_routes = sorted(all_routes, key=lambda x: int(ipaddress.ip_network(x['prefix']).network_address))

        for route in sorted_routes:
            if route['interface']:
                print(f"{route['code']}    {route['prefix']} is directly connected, {route['interface']}", end='')
            elif route['code'] == 'L':
                print(f"{route['code']}    {route['prefix']} is directly connected", end='')
            elif not route['next_hops']:
                print(f"{route['code']}    {route['prefix']}", end='')
            else:
                if len(route['next_hops']) > 1:
                    first_hop = route['next_hops'][0]
                    print(f"{route['code']}    {route['prefix']} [{route['preference']}/{route['metric']}] via {first_hop['ip']}", end='')
                    
                    if first_hop['interface']:
                        print(f", {first_hop['interface']}", end='')
                    
                    if route['uptime']:
                        print(f", {route['uptime']}", end='')
                    
                    for next_hop in route['next_hops'][1:]:
                        print(f"\n           [{route['preference']}/{route['metric']}] via {next_hop['ip']}", end='')
                        
                        if next_hop['interface']:
                            print(f", {next_hop['interface']}", end='')
                        
                        if route['uptime']:
                            print(f", {route['uptime']}", end='')
                else:
                    first_hop = route['next_hops'][0]
                    print(f"{route['code']}    {route['prefix']} [{route['preference']}/{route['metric']}] via {first_hop['ip']}", end='')
                    
                    if first_hop['interface']:
                        print(f", {first_hop['interface']}", end='')
                    
                    if route['uptime']:
                        print(f", {route['uptime']}", end='')
            
            print()

        print(f"\n-> Try 'show network-instance {network_instance} route-table' for the best insights.")

    def _get_route_code(self, route_type, route_owner):
        if route_type == 'host':
            return 'L'
        if route_type == 'local':
            return 'C'

        codes = {
            'aggregate': 'Ag',
            'arp-nd': 'Ar',
            'bgp': 'B',
            'bgp-label': 'BL',
            'bgp-evpn': 'BE',
            'bgp-vpn': 'BV',
            'dhcp': 'D',
            'gribi': 'G',
            'host': 'H',
            'isis': 'IS',
            'linux': 'Li',
            'ndk1': 'N1',
            'ndk2': 'N2',
            'ospfv2': 'O',
            'ospfv3': 'O',
            'static': 'S',
        }
        return codes.get(route_type.lower(), '?')
