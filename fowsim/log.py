from django.views.debug import ExceptionReporter


class AddRequestBodyExceptionReporter(ExceptionReporter):
    def get_traceback_data(self):
        data = super().get_traceback_data()

        #  add body if it exists
        if self.request is not None:
            if self.request.method == "POST":
                try:
                    data["request_body"] = self.request.body
                except Exception:
                    data["request_body"] = None
        return data
