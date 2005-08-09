
def run_unit_tests(pusher):
    codir = pusher.checkout_dir()
    (out,err) = pusher.execute("pushd %s && py.test && popd" % codir)
    return ("failed" not in out,out,err)
