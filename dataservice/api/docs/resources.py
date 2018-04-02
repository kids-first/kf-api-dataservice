import glob
from flask.views import View
from flask import jsonify, current_app, render_template, send_file


class Documentation(View):
    def dispatch_request(self):
        return render_template('redoc.html')


class Logo(View):
    def dispatch_request(self):
        return send_file('../docs/dataservice.png')


class Swagger(View):
    """
    Swagger spec resource

    Generates the swagger spec and distributes it through an endpoint
    """

    def __init__(self, **kwargs):
        super(Swagger, self).__init__(**kwargs)
        self.spec = None

    def dispatch_request(self):
        """
        Creates the spec and augments it with resource descriptions from
        loading in READMEs inside each resource's directory.

        Will only generate the spec once, then cache it.
        """
        if self.spec:
            return jsonify(self.spec)

        self.spec = current_app.spec.to_dict()
        with open('dataservice/api/README.md') as f:
            self.spec['info']['description'] = f.read()

        tags = []
        for d in glob.glob('dataservice/api/*/README.md'):
            name = d.split('/')[-2].capitalize()
            tag = {
                'name': name.capitalize(),
                'description': open(d, 'r').read()
            }
            tags.append(tag)

        self.spec['tags'] = tags
        self.spec['info']['x-logo'] = {'url': '/logo'}

        return jsonify(self.spec)
