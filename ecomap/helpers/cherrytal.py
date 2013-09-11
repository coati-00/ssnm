from simpletal import simpleTAL, simpleTALES
import cStringIO
import os, cherrypy, os.path

def site_root():
    return os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__),"../../")))

import logging
l = logging.getLogger("simpleTAL.XMLTemplateCompiler")
l.setLevel(50)


class CherryTAL:
    """ a class that can be inherited from to easily use
    simpleTAL templates from a CherryPy app
    """
    _template_dir = "templates"
    _globals = {}
    _macros_file = "macros.pt"
    _allow_python_path = 1


    def template(self, filename, data):
        context = simpleTALES.Context(allowPythonPath=self._allow_python_path)

        context.addGlobal('message',cherrypy.session.get("message",""))
        cherrypy.session['message'] = ""
        for k in self._globals.keys():
            context.addGlobal(k,self._globals[k])

        for k in data.keys():
            context.addGlobal(k,data[k])


        # if there's a macros.pt file, we load that
        macrosfile = open(os.path.join(site_root(),self._template_dir + os.sep + self._macros_file),
                'r')
        macros = simpleTAL.compileXMLTemplate(macrosfile)
        macrosfile.close()
        context.addGlobal("sitemacros",macros)

        templatefile = open(os.path.join(site_root(),self._template_dir + os.sep + filename), 'r')
        template = simpleTAL.compileXMLTemplate(templatefile)
        templatefile.close()
        fakeout = cStringIO.StringIO()
        template.expand(context, fakeout)
        fakeout.seek(0)
        return fakeout.read()
