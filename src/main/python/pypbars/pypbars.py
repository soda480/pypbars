import logging
from list2term import Lines
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

    def __init__(self, regex=None, log_write=True, lookup=None, show_index=True, use_color=True, **kwargs):
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
        self._mirror = []
        data = []
        for _ in range(size):
            progress_bar = ProgressBar(regex=regex, control=True, use_color=use_color, **kwargs)
            data.append(progress_bar)
            self._mirror.append(str(progress_bar))
        self._log_write = log_write
        super().__init__(data=data, size=size, lookup=lookup, show_index=show_index, use_color=use_color)

    def print_line(self, index, force=False):
        super().print_line(index, force=force)
        self._mirror[index] = str(self[index])

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
                if str(self[index]) == self._mirror[index]:
                    logger.debug(f'skipping print - the progress bar at index {index} has not changed after match')
                else:
                    self.print_line(index)
            if self[index].complete:
                # print the progress bar when it completes
                self.print_line(index)
        if self._log_write:
            logger.debug(item)
