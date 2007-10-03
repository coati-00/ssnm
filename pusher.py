
#def run_unit_tests(pusher):
#    codir = pusher.checkout_dir()
#    (out,err) = pusher.execute("pushd %s && python setup.py testgears && popd" % codir)
#    return ("FAILED" not in out,out,err)

def post_rsync(pusher):
    """ restart apache2 """
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/rm","/var/www/ecomap/eggs/psycopg2-2.0.6-py2.5-linux-x86_64.egg"])
    (out,err) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/var/www/ecomap/init.sh","/var/www/ecomap/"])
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","/bin/ln","-s","/usr/lib/python2.5/site-packages/psycopg2/","/var/www/ecomap/working-env/lib/python2.5/"])
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","ssnm"])
    (out2,err2) = pusher.execute(["ssh","monty.ccnmtl.columbia.edu","sudo","/usr/bin/supervisorctl","restart","hope"])    
    
    out += out2
    err += err2
    return (True,out,err)  
