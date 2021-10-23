'''Prepare device structure from configuration file by applying type inheritance
and other preprocessing steps.'''

from copy import deepcopy


def _push_dev_settings_to_channels(devs):
    '''Push settings from device level down to channel level.'''

    for dev in devs.values():
        for name, val in dev.items():
            if not isinstance(val, dict):
                for channel in dev['channels'].values():
                    if name not in channel:
                        channel[name] = dev[name]


def _inherit_from_types(types, devs):
    '''Inherit settings from types to devices.'''

    for devname, dev in devs.items():
        for devtype in dev['types']:
            if devtype not in  types:
                msg = "Device '{0}' references an undefined type '{1}'."
                raise Exception(msg.format(devname, devtype))

            typ = types[devtype]

            # update channels from type to device
            for chname, channel in typ['channels'].items():
                if chname not in dev['channels']:
                    dev['channels'][chname] = deepcopy(channel)

            for name, val in typ.items():
                # all value types can be inherited, but no structures
                if not isinstance(val, dict) and (name not in dev):
                    dev[name] = val


def _set_name_attribute(devs):
    '''Add _name attribute from dictionary key to devices and channels.'''

    for devname, dev in devs.items():
        dev['_dev_name'] = devname

        for chname, channel in dev['channels'].items():
            channel['_ch_name'] = chname


def _split_topics(devs):
    '''Convert string topics to lists (split at /).'''

    for dev in devs.values():
        for channel in dev['channels'].values():
            channel['topic'] = channel['topic'].split('/')


def prepare_devices(dev_cfg):
    '''Preprocess devices, i.e. apply type inheritance, push device settings
    to channels, and put name attribute to devices and channels.'''

    # push down type settings to type channels
    _push_dev_settings_to_channels(dev_cfg['types'])

    # inverit from types to devices
    _inherit_from_types(
        types=dev_cfg['types'],
        devs=dev_cfg['devices'])

    # push down device settings to channels
    _push_dev_settings_to_channels(dev_cfg['devices'])

    # put name as key / value pair to devices and channels
    _set_name_attribute(dev_cfg['devices'])

    # split topic strings
    _split_topics(dev_cfg['devices'])
