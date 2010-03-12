class AppendingList(list):

    def __init__(self, *a, **k):
        list.__init__(self, *a ,**k)

    def __call__(self, *a):
        if len(a):
            self.extend(a)
            print(a)
        return self

class MessagesMiddleware(object):
    """This middleware augments the FlashMiddleware by pre-creating the lists
    for 'messages', 'error' and 'warning'
    """

    def process_request(self, request):
        """Add any missing lists to the flash"""
        flash = request.flash
        if not 'messages' in flash:
            flash['messages'] = AppendingList()
        if not 'warnings' in flash:
            flash['warnings'] = AppendingList()
        if not 'errors' in flash:
            flash['errors'] = AppendingList()

#    def process_response(self, request, response):
#        """This method is called by the Django framework when a *response* is
#sent back to the user.
#"""
#        flash = request.flash
#        print "E: %s" % flash['errors']
#        print "W: %s" % flash['warnings']
#        print "M: %s" % flash['messages']
#        return response