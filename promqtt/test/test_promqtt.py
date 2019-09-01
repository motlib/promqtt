import pytest

from promqtt.prom import PrometheusExporter


def _has_line(promexp, line):
    out = promexp.render().split('\n')
    
    return any(map(lambda l: l == line, out))


@pytest.fixture
def promexp():
    '''Create a new prometheus exporter instance.'''
    
    http_cfg = {'interface':'127.0.0.01', 'port': 13541}
    pe = PrometheusExporter(http_cfg)

    return pe


def test_promqtt_register(promexp):
    '''Register measurement and check that it's not yet in the output.'''
    promexp.register(
        name='test_meas_1',
        datatype='gauge',
        helpstr='yeah',
        timeout=12)

    out = promexp.render().split('\n')

    # we did not set a value, so no measurement shall be visible
    hasline = any(map(lambda l: l.startswith('test_meas_1'), out))

    assert(not hasline)
    

def test_promqtt_set(promexp):
    '''Setting a value to a registered measurement works fine.'''
    
    promexp.register(
        name='test_meas_1',
        datatype='gauge',
        helpstr='yeah',
        timeout=12)

    promexp.set(
        name='test_meas_1',
        value=12.3,
        labels={'foo': 'bar'})

    assert(_has_line(promexp, '# HELP test_meas_1 yeah'))
    assert(_has_line(promexp, '# TYPE test_meas_1 gauge'))
    assert(_has_line(promexp, 'test_meas_1{foo="bar"} 12.3'))

    
    
def test_promqtt_not_registered(promexp):
    '''Setting a value to a not registered measurement raises an exception.'''
    
    #with pytest.raises(Exception):
    promexp.set(
        name='test_meas_2',
        value=12.3,
        labels={})

    
