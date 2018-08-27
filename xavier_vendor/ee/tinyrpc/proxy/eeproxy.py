#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpcproxy import RPCProxy
from ee.tinyrpc.exc import RPCError


class EEProxy(RPCProxy):
    """Client for making RPC calls to connected servers.

    :param protocol: An :py:class:`~tinyrpc.RPCProtocol` instance.
    :param transport: A :py:class:`~tinyrpc.transports.ClientTransport`
                      instance.
    """

    def __init__(self, protocol, transport):
        super(EEProxy, self).__init__()
        self.protocol = protocol
        self.transport = transport

    def _send_and_handle_reply(self, req):
        # sends and waits for reply
        reply = self.transport.send_message(req.serialize())
        response = self.protocol.parse_reply(reply)
        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response

    def call(self, method, args, kwargs, one_way=False):
        """Calls the requested method and returns the result.

        If an error occured, an :py:class:`~tinyrpc.exc.RPCError` instance
        is raised.

        :param method: Name of the method to call.
        :param args: Arguments to pass to the method.
        :param kwargs: Keyword arguments to pass to the method.
        :param one_way: Whether or not a reply is desired.
        """
        #print 'create_request: ', self.protocol.create_request
        req = self.protocol.create_request(method, args, kwargs, one_way)
        return self._send_and_handle_reply(req).result

    def batch_call(self, calls):
        """Experimental, use at your own peril."""
        req = self.protocol.create_batch_request()

        for call_args in calls:
            req.append(self.protocol.create_request(*call_args))

        return self._send_and_handle_reply(req)

    def reconnect(self):
        self.transport.reconnect()
