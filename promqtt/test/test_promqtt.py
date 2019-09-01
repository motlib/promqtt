import pytest

from promqtt.prom import PrometheusExporter


@pytest.fixture
def promexp():
    http_cfg = {'interface':'127.0.0.01', 'port': 13541}
    pe = PrometheusExporter(http_cfg)

    return pe

def test_promqtt_register(promexp):
    promexp.register(
        name='test_meas_1',
        datatype='gauge',
        helpstr='yeah',
        timeout=12)

    out = promexp.render().split('\n')

    # we did not set a value, so no measurement shall be visible
    hasline = any(map(lambda l: l.startswith('test_meas_1'), out))

    assert(not hasline)
    

# Example 
# # HELP tasmota_humidity Relative humidity in percent
# # TYPE tasmota_humidity gauge
# tasmota_humidity{node="sens-bathroom-1",sensor="BME280"} 63.8
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

    out = promexp.render().split('\n')
    
    assert(any(map(lambda l: l.startswith('# HELP test_meas_1 yeah'), out)))
    assert(any(map(lambda l: l.startswith('# TYPE test_meas_1 gauge'), out)))
    assert(any(map(lambda l: l.startswith('test_meas_1{foo="bar"} 12.3'), out)))

    
    
def test_promqtt_not_registered(promexp):
    '''Setting a value to a not registered measurement raises an exception.'''
    
    #with pytest.raises(Exception):
    promexp.set(
        name='test_meas_2',
        value=12.3,
        labels={})

    
def test_promqtt_register2(promexp):
    out = promexp.render()
    
    hasline = any(map(lambda l: l.startswith('test_meas_1'), out.split('\n')))

    assert(not hasline)

