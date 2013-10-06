def get_handler_constructor(handlers):
    def constructor(signal):
        assert signal not in handlers, "Handler for signal {} already exsists".format(signal)

        def wraper(func):
            handlers[signal] = func
            return func

        return wraper

    return constructor

