
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && py.test && popd" % codir)
    return ("failed" not in out,out,err)

def post_rsync(pusher):
    """ restart apache2 """
    (out,err) = pusher.execute(["ssh","frink.ccnmtl.columbia.edu","sudo","/etc/init.d/apache2","restart"])
    return (True,out,err)
