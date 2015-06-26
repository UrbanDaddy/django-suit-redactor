# from django.core.serializers import json
from django.forms import Textarea
from django.utils.safestring import mark_safe

try: import json
except ImportError: import django.utils.simplejson as json


class RedactorWidget(Textarea):
    class Media:
        css = {
            'all': ('suit-redactor/redactor/redactor.css',)
        }
        js = ('suit-redactor/redactor/redactor.min.js',)

    def __init__(self, attrs=None, editor_options={}):
        super(RedactorWidget, self).__init__(attrs)
        self.editor_options = editor_options


    def render(self, name, value, attrs=None):
        output = super(RedactorWidget, self).render(name, value, attrs)

        # When you embed an inline for a many-to-one model, Django generates an
        # 'empty' version of the inline form to serve as a template. The markup
        # might look like:
        #
        #     <div id="some-form-0">...<input name="some-widget-0">...</div>
        #     <div id="some-form-__prefix__ empty">...<input name="some-widget-__prefix__">...</div>
        #
        # When you 'Add another Foo', the JavaScript in Django's admin copies
        # the empty form and does a string replacement on all the nodes with
        # '__prefix__' and gives them a new index. After this is done, the
        # markup might look like:
        #
        #     <div id="some-form-0">...<input name="some-widget-0">...</div>
        #     <div id="some-form-1">...<input name="some-widget-1">...</div>
        #     <div id="some-form-__prefix__ empty">...<input name="some-widget-__prefix__">...</div>
        #
        # The Redactor initialization must not be run when it's in an empty
        # form because it makes changes to the DOM. When the new inline form is
        # created, the Redactor initialization must then be run. When the
        # initialization is run twice (once in the empty form and then again
        # when the form is copied), you'll end up with the following problem in
        # some-form-1.
        #
        #     <div id="some-form-0">
        #         ...
        #         <div class="some-redactor-thing-0">...</div>
        #         <input name="some-widget-0">
        #         <script>$('#some-form-0").redactor()</script>
        #         ...
        #     </div>
        #     <div id="some-form-1">
        #         ...
        #         <div class="some-redactor-thing-__prefix__">...</div>
        #         <div class="some-redactor-thing-1">...</div>
        #         <input name="some-widget-1">
        #         <script>$('#some-form-1").redactor()</script>
        #         ...
        #     </div>
        #     <div id="some-form-__prefix__">
        #         ...
        #         <div class="some-redactor-thing-__prefix__">...</div>
        #         <input name="some-widget-__prefix__">
        #         <script>$('#some-form-__prefix__").redactor()</script>
        #         ...
        #     </div>
        #
        # In JavaScript we check for '__prefix__' in the ID so that the
        # Redactor initialization isn't run in the empty (template) form.
        output += mark_safe("""
            <script type="text/javascript">
                (function ($) {{
                    var id = '#id_{}';
                    if (id.indexOf('__prefix__') < 0) {{
                        $(id).redactor({});
                    }}
                }}(django.jQuery));
            </script>
        """.format(name, json.dumps(self.editor_options)))
        return output
