from bigsuds import ServerError
import f5
import f5.util
import re

class CachedFactory(f5.util.CachedFactory):
    def create(self, nodeportpools, lb=None, *args, **kwargs):
        objects = []

        for nps in nodeportpools:
            key = nps[0].name + str(nps[1]) + nps[2].name
            if lb is not None:
                key = lb.host + key
    
            # Save some bytes
            key = hash(key)
    
            if key in self._cache:
                objects.append(self._cache[key])
            else:
                obj = self._Klass(nps[0], nps[1], nps[2], *args, lb=lb, **kwargs)
    
                self._cache[key] = obj
                objects.append(obj)
        return objects

    def put(self, obj):
        key = obj.node.name + str(obj.port) + obj.pool.name
        if obj.lb is not None:
            key = obj.lb.host + key

        key = hash(key)
        self._cache[key] = obj


class PoolMember(object):
    __version = 11

    def __init__(self, node, port, pool, lb=None, connection_limit=None, description=None,
            dynamic_ratio=None, enabled=None, priority=None, rate_limit=None, ratio=None):

        if lb is not None and not isinstance(lb, f5.Lb):
            raise ValueError('lb must be of type f5.Lb, not %s' % (type(lb).__name__))

        # Make sure we're dealing with objects
        if isinstance(node, str):
            node = f5.Node(node, lb)
        if isinstance(pool, str):
            pool = f5.Pool(pool, lb)

        self._lb               = lb
        self._node             = node
        self._pool             = pool
        self._port             = port
        self._address          = node._address
        self._connection_limit = connection_limit
        self._description      = description
        self._dynamic_ratio    = dynamic_ratio
        self._enabled          = enabled
        self._priority         = priority
        self._rate_limit       = rate_limit
        self._ratio            = ratio

        if self._lb:
            self._set_wsdl()

    def __repr__(self):
        return "f5.PoolMember('%s', %s, '%s')" % (self._node, self._port, self._pool)

    ###########################################################################
    # Private API
    ###########################################################################
    def _set_wsdl(self):
            self.__wsdl = self._get_wsdl(self._lb)

    @staticmethod
    def _get_wsdl(lb):
        return lb._transport.LocalLB.Pool

    @f5.util.lbmethod
    def _get_addrport(self):
        return {'address': self._node.name, 'port': self._port}

    @f5.util.lbmethod
    def _get_address(self):
        return self.__wsdl.get_member_address([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_connection_limit(self):
        return self.__wsdl.get_member_connection_limit([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_description(self):
        return self.__wsdl.get_member_description([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_dynamic_ratio(self):
        return self.__wsdl.get_member_dynamic_ratio([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_priority(self):
        return self.__wsdl.get_member_priority([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_rate_limit(self):
        return self.__wsdl.get_member_rate_limit([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_ratio(self):
        return self.__wsdl.get_member_ratio([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbmethod
    def _get_object_status(self):
        return self.__wsdl.get_member_object_status([self._pool.name], [[self._get_addrport()]])[0][0]

    @f5.util.lbwriter
    def _set_description(self, value):
        self.__wsdl.set_member_description([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_connection_limit(self, value):
        self.__wsdl.set_member_connection_limit([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_dynamic_ratio(self, value):
        self.__wsdl.set_member_dynamic_ratio([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_priority(self, value):
        self.__wsdl.set_member_priority([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_rate_limit(self, value):
        self.__wsdl.set_member_rate_limit([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_ratio(self, value):
        self.__wsdl.set_member_ratio([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _set_session_enabled_state(self, value):
        self.__wsdl.set_member_session_enabled_state([self._pool.name], [[self._get_addrport()]], [[value]])

    @f5.util.lbwriter
    def _create(self):
        self.__wsdl.add_member_v2([self._pool.name], [[self._get_addrport()]])

    @f5.util.lbwriter
    def _remove(self):
        self.__wsdl.remove_member_v2([self._pool.name], [[self._get_addrport()]])

    @classmethod
    def _get_list(cls, lb, pools):
        return cls._get_wsdl(lb).get_member_v2(pools)

    @classmethod
    def _get_addresses(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_address(pools, ipaddrsq2)

    @classmethod
    def _get_connection_limits(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_connection_limit(pools, ipaddrsq2)

    @classmethod
    def _get_descriptions(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_description(pools, ipaddrsq2)

    @classmethod
    def _get_dynamic_ratios(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_dynamic_ratio(pools, ipaddrsq2)

    @classmethod
    def _get_priorities(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_priority(pools, ipaddrsq2)

    @classmethod
    def _get_rate_limits(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_rate_limit(pools, ipaddrsq2)

    @classmethod
    def _get_ratios(cls, lb, pools, ipaddrsq2):
        return cls._get_wsdl(lb).get_member_ratio(pools, ipaddrsq2)

    @classmethod
    def _get_objects(cls, lb, pools, addrportsq2, minimal=False):

        # F5 skips empty lists in the sequence causing a mismatch in list indices,
        # so we have to remove empty pools before  we can fetch other attributes.
        f5.util.prune_f5_lists(addrportsq2, pools)

        # Return an empty list if we pruned all pools (i.e. all pools were empty)
        if not pools:
            return []

        pools = f5.Pool.factory.create(pools, lb)
        if not minimal:
            address2          = cls._get_addresses(lb, pools, addrportsq2)
            connection_limit2 = cls._get_connection_limits(lb, pools, addrportsq2)
            description2      = cls._get_descriptions(lb, pools, addrportsq2)
            dynamic_ratio2    = cls._get_dynamic_ratios(lb, pools, addrportsq2)
            priority2         = cls._get_priorities(lb, pools, addrportsq2)
            rate_limit2       = cls._get_rate_limits(lb, pools, addrportsq2)
            ratio2            = cls._get_ratios(lb, pools, addrportsq2)

        for idx, addrportsq in enumerate(addrportsq2):
            nodes = f5.Node.factory.create([addrport['address'] for addrport in addrportsq], lb)
            poolmembers = cls.factory.create(
                    [[nodes[_idx], addrport['port'], pools[idx]]
                        for _idx,addrport in enumerate(addrportsq)], lb)

            for idx_inner, pm in enumerate(poolmembers):
                if not minimal:
                    pm._address          = address2[idx][idx_inner]
                    pm._connection_limit = connection_limit2[idx][idx_inner]
                    pm._description      = description2[idx][idx_inner]
                    pm._dynamic_ratio    = dynamic_ratio2[idx][idx_inner]
                    pm._priority         = priority2[idx][idx_inner]
                    pm._rate_limit       = rate_limit2[idx][idx_inner]
                    pm._ratio            = ratio2[idx][idx_inner]

        return poolmembers

    @classmethod
    def _get(cls, lb, pools=None, pattern=None, minimal=False):
        if pools is not None:
            if isinstance(pools, list):
                pools = [pool.name for pool in pools]
            else:
                pools = [pools]
        else:
            pools = f5.Pool._get_list(lb)

        addrportsq2 = cls._get_list(lb, pools)

        if pattern is not None:
            if not isinstance(pattern, re._pattern_type):
                pattern = re.compile(pattern)
            for idx,addrportsq in enumerate(addrportsq2):
                addrportsq2[idx] = filter(
                        lambda ap: pattern.match('%s:%s' % (ap['address'], ap['port'])), addrportsq)

        return cls._get_objects(lb, pools, addrportsq2, minimal)

    ###########################################################################
    # Properties
    ###########################################################################
    #### lb ####
    @property
    def lb(self):
        return self._lb

    @lb.setter
    @f5.util.updatefactorycache
    def lb(self, value):
        if value is not None and not isinstance(value, f5.Lb):
            raise ValueError('lb must be of type lb, not %s' % (type(value).__name__))

        self._lb = value
        self._set_wsdl()

        # Also update the node's lb <- not sure (yet) if this is the right thing
        self._node.lb = value

    #### address ####
    @property
    def address(self):
        if self._lb:
            self._address = self._get_address()
        return self._address

    #### node ####
    @property
    def node(self):
       return self._node

    @node.setter
    @f5.util.updatefactorycache
    def node(self, value):
        if self._lb:
            raise AttributeError("set attribute node not allowed when linked to lb")

        if isinstance(value, str):
            value = f5.Node(name=value, lb=self._lb)

        self._node = value

    #### port ####
    @property
    def port(self):
       return self._port

    @port.setter
    @f5.util.updatefactorycache
    def port(self, value):
        if self._lb:
            raise AttributeError("set attribute port not allowed when linked to lb")

        self._port = value

    #### pool ####
    @property
    def pool(self):
       return self._pool

    @pool.setter
    @f5.util.updatefactorycache
    def pool(self, value):
        if self._lb:
            raise AttributeError("set attribute pool not allowed when linked to lb")

        self._pool = value

    #### connection_limit ####
    @property
    def connection_limit(self):
       if self._lb:
           self._connection_limit = self._get_connection_limit()
       return self._connection_limit

    @connection_limit.setter
    def connection_limit(self, value):
        if self._lb:
            self._set_connection_limit(value)

        self._connection_limit = value

    #### description ####
    @property
    def description(self):
       if self._lb:
           self._description = self._get_description()
       return self._description

    @description.setter
    def description(self, value):
        if self._lb:
            self._set_description(value)

        self._description = value

    #### dynamic_ratio ####
    @property
    def dynamic_ratio(self):
       if self._lb:
           self._dynamic_ratio = self._get_dynamic_ratio()
       return self._dynamic_ratio

    @dynamic_ratio.setter
    def dynamic_ratio(self, value):
        if self._lb:
            self._set_dynamic_ratio(value)

        self._dynamic_ratio = value

    #### priority ####
    @property
    def priority(self):
       if self._lb:
           self._priority = self._get_priority()

       return self._priority

    @priority.setter
    def priority(self, value):
        if self._lb:
            self._set_priority(value)
        self._priority = value

    #### rate_limit ####
    @property
    def rate_limit(self):
       if self._lb:
           self._rate_limit = self._get_rate_limit()
       return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value):
        if self._lb:
            self._set_rate_limit(value)

        self._rate_limit = value

    #### ratio ####
    @property
    def ratio(self):
       if self._lb:
           self._ratio = self._get_ratio()
       return self._ratio

    @ratio.setter
    def ratio(self, value):
        if self._lb:
            self._set_ratio(value)

        self._ratio = value

    #### enabled ####
    @property
    # TODO: There are more states than true/false, what do we do ?
    def enabled(self):
        if self._lb:
            enabled_status = self._get_object_status()['enabled_status']
            if enabled_status == 'ENABLED_STATUS_ENABLED':
                self._enabled = True
            elif enabled_status == 'ENABLED_STATUS_DISABLED_BY_PARENT':
                self._enabled = True
            elif enabled_status == 'ENABLED_STATUS_DISABLED':
                self._enabled = False
            else:
                raise RuntimeError("Unknown enabled_status received for poolmember: '%s'" % enabled_status)

        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if value == True:
            enabled_status = 'STATE_ENABLED'
        elif value == False:
            enabled_status = 'STATE_DISABLED'
        else:
            raise ValueError('enabled must be either True or False')

        if self._lb:
            self._set_session_enabled_state(enabled_status)

        self._enabled = value

    ###########################################################################
    # Public API
    ###########################################################################
    @f5.util.lbtransaction
    def save(self):
        """Save the poolmember to the lb"""
        if not self.exists():
            self._create()

        if self._connection_limit is not None:
            self.connection_limit = self._connection_limit
        if self._description is not None:
            self.description = self._description
        if self._dynamic_ratio is not None:
            self.dynamic_ratio = self._dynamic_ratio
        if self._enabled is not None:
            self.enabled = self._enabled
        if self._priority is not None:
            self.priority = self._rate_limit
        if self._rate_limit is not None:
            self.rate_limit = self._rate_limit
        if self._ratio is not None:
            self.ratio = self._ratio

    def delete(self):
        """Delete the poolmember from the lb"""
        self._remove()

    def exists(self):
        """Check if poolmember exists on the lb"""
        try:
            self._get_description()
        except ServerError as e:
            if 'was not found' in e.message:
                return False
            else:
                raise
        except:
            raise

        return True

    def refresh(self):
        """Fetch all attributes from the lb"""
        self.address
        self.connection_limit
        self.description
        self.dynamic_ratio
        self.enabled
        self.priority
        self.rate_limit
        self.ratio

PoolMember.factory = CachedFactory(PoolMember)
