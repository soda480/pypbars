import unittest
from mock import patch
from mock import call
from mock import Mock
from mock import MagicMock

from pypbars import ProgressBars


class TestProgressBars(unittest.TestCase):

    def test__init_Should_RaiseValueError_When_DataAttributeProvided(self, *patches):
        with self.assertRaises(ValueError):
            ProgressBars(data=['one', 'two', 'three'])

    def test__init_Should_RaiseValueError_When_SizeAttributeProvided(self, *patches):
        with self.assertRaises(ValueError):
            ProgressBars(size=3)

    def test__init_Should_RaiseValueError_When_LookupAttributeIsNotProvided(self, *patches):
        with self.assertRaises(ValueError):
            ProgressBars()

    @patch('pypbars.pypbars.ProgressBar')
    def test__init_Should_SetAttributes_When_Called(self, progress_bar_patch, *patches):
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        self.assertEqual(len(pbars.data), len(lookup))
        self.assertEqual(pbars.data[0], progress_bar_patch.return_value)
        self.assertTrue(pbars._log_write)

    @patch('pypbars.pypbars.ProgressBar')
    def test__init_Should_CallProgressBarWithDefaultValues_When_RegexAttributeNotProvided(self, progress_bar_patch, *patches):
        lookup = ['one', 'two', 'three']
        ProgressBars(lookup=lookup)
        progress_bar_patch.assert_called_with(regex=ProgressBars.regex, control=True, use_color=True)

    @patch('pypbars.pypbars.ProgressBar')
    def test__init_Should_CallProgressBarWithUserProvidedValues_When_RegexAndFillAttributeProvided(self, progress_bar_patch, *patches):
        lookup = ['one', 'two', 'three']
        ProgressBars(lookup=lookup, regex='--regex--', use_color=False)
        progress_bar_patch.assert_called_with(regex='--regex--', control=True, use_color=False)

    @patch('pypbars.ProgressBars.get_index_message', return_value=(None, None))
    @patch('pypbars.pypbars.logger')
    def test_write_Should_LogItem_When_LogWriteAttributeTrue(self, logger_patch, *patches):
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        message = 'some message'
        pbars.write(message)
        logger_patch.debug.assert_called_with(message)

    @patch('pypbars.pypbars.logger')
    @patch('pypbars.ProgressBars.get_index_message', return_value=(2, '--matched sub-message--'))
    @patch('pypbars.ProgressBars.print_line')
    @patch('pypbars.pypbars.ProgressBar')
    def test_write_Should_PrintLine_When_IndexMatch(self, progress_bar_patch, print_line_patch, *patches):
        progress_bar_mock = Mock(complete=False)
        progress_bar_mock.match.return_value = True
        progress_bar_patch.return_value = progress_bar_mock
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        pbars._mirror[2] = '---'
        pbars.write('')
        print_line_patch.assert_called_once_with(2)

    @patch('pypbars.pypbars.logger')
    @patch('pypbars.ProgressBars.get_index_message', return_value=(2, '--matched sub-message--'))
    @patch('pypbars.ProgressBars.print_line')
    @patch('pypbars.pypbars.ProgressBar')
    def test_write_Should_PrintLine_When_IndexMatchAndProgressBarIsComplete(self, progress_bar_patch, print_line_patch, *patches):
        progress_bar_mock = Mock(complete=True)
        progress_bar_mock.match.return_value = True
        progress_bar_patch.return_value = progress_bar_mock
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        pbars._mirror[2] = '---'
        pbars.write('')
        self.assertEqual(len(print_line_patch.mock_calls), 2)

    @patch('pypbars.pypbars.logger')
    @patch('pypbars.ProgressBars.get_index_message', return_value=(2, '--matched sub-message--'))
    @patch('pypbars.ProgressBars.print_line')
    @patch('pypbars.pypbars.ProgressBar')
    def test_write_Should_NotPrintLine_When_IndexMatchButMirrorIsSame(self, progress_bar_patch, print_line_patch, *patches):
        progress_bar_mock = Mock(complete=False)
        progress_bar_mock.match.return_value = True
        progress_bar_patch.return_value = progress_bar_mock
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        pbars.write('')
        print_line_patch.assert_not_called()

    @patch('pypbars.pypbars.ProgressBar', return_value='')
    def test__print_line_Should_UpdateMirror_When_Called(self, *patches):
        lookup = ['one', 'two', 'three']
        pbars = ProgressBars(lookup=lookup)
        pbars.print_line(0)
