from subprocess import check_output, CalledProcessError

def getSnmp(host,OID):
    if host is not None:
        try:
            raw = check_output(["snmpget", "-v2c", "-cqwsxczasde", host, OID])
            return re.sub('^.*STRING: ','',raw).strip()
        except CalledProcessError:
            return None
    else:
        return None
