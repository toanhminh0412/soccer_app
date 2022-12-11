# Display success or error message if any
class MessageViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Display success or error message if any
        context['success'] = self.request.session.get('success', None)
        context['message'] = self.request.session.get('message', None)
        if context['success'] is not None:
            del self.request.session['success']
            del self.request.session['message']

        return context