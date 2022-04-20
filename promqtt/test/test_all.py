


def test_all():
    '''Complete system test'''



    cfgfile = os.environ.get('PROMQTT_CONFIG', 'promqtt.yml')
    cfg = load_config(cfgfile)

    promexp = PrometheusExporter()
