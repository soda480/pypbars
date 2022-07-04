import logging
from l2term import Lines
from progress1bar import ProgressBar

logger = logging.getLogger(__name__)


class ProgressBars(Lines):
    """ display multiple progress bars on the terminal
    """
    regex = {
        'total': r'^processing total of (?P<value>\d+) items$',
        'count': r'^processed .*$',
        'alias': r'^worker is (?P<value>.*)$'
    }

    def __init__(self, regex=None, log_write=True, lookup=None, show_index=True, **kwargs):
        """ constructor
        """
        logger.debug('executing ProgressBars constructor')
        if kwargs.get('data'):
            # data list will be constructed by this class
            raise ValueError('specifying data is not supported')
        if kwargs.get('size'):
            # size will be determined from length of lookup list
            raise ValueError('specifying size is not supported')
        if not lookup:
            raise ValueError('a lookup attribute is required')
        if not regex:
            regex = ProgressBars.regex
        size = len(lookup)
        data = []
        for _ in range(size):
            data.append(ProgressBar(regex=regex, control=True, **kwargs))
        self._log_write = log_write
        super().__init__(data=data, size=size, lookup=lookup, show_index=show_index)

    def write(self, item):
        """ update appropriate progress bar as specified by item if applicable
            check if item contains directed message for an identity
            the index for the progress bar is determined using the extracted identity with the lookup table
            provided during instantiation
            override parent method
        """
        index, message = self.get_index_message(item)
        if index is not None:
            if self[index].match(message):
                self.print_line(index)
            if self[index].complete:
                # print the progress bar when it completes
                self.print_line(index)
        if self._log_write:
            logger.debug(item)
