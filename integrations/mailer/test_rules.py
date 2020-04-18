'''
Unit test definitions for all rules
'''
import pytest
import mailer
from alertaclient.models.alert import Alert
from mock import MagicMock, patch, DEFAULT


def test_rules_dont_exist():
    '''
    Test the rules file is read
    '''
    with patch('mailer.os') as system_os:
        system_os.path.exists.return_value = False
        res = mailer.parse_group_rules('config_file')
        system_os.path.exists.called_once_with('confile_file')
        # assert res is None


def test_rules_parsing():
    '''
    Test the rules file is properly read
    '''
    with patch.multiple(mailer, os=DEFAULT, open=DEFAULT,
                        json=DEFAULT, validate_rules=DEFAULT) as mocks:
        mocks['os'].path.exists.return_value = True
        mocks['os'].walk().__iter__\
            .return_value = [('/', None,
                              ['cantopen.json', 'invalid.json', 'valid.json'])]
        invalid_file = MagicMock()
        valid_file = MagicMock()
        mocks['open'].side_effect = [IOError, invalid_file, valid_file]
        doc = [{'notify': {'fields': []}}]
        mocks['json'].load.side_effect = [TypeError, doc]
        mocks['validate_rules'].return_value = doc
        res = mailer.parse_group_rules('config_file')

        # Assert that we checked for folder existence
        mocks['os'].path.exists.called_once_with('confile_file')

        # Check that validation was called for valid file
        mocks['validate_rules'].assert_called_once_with(doc)
        assert mocks['validate_rules'].call_count == 1

        # Assert that we tried to open all 3 files
        assert mocks['open'].call_count == 3
        # Assert that we tried to load 2 files only
        assert mocks['json'].load.call_count == 2
        # Assert that we have proper return value
        assert res == doc


TESTDOCS = [
    ('', False),
    ('String', False),
    ({}, False),
    ([], True),
    ([
        {"name": "invalid_no_fields",
         "contacts": []}
    ], False),
    ([
        {"name": "invalid_empty_fields",
         "fields": [],
         "contacts": []}
    ], False),
    ([
        {"name": "invalid_no_contacts",
         "fields": [{"field": "resource", "regex": r"\d{4}"}]}
    ], False),
    ([
        {"name": "invalid_no_field_on_fields",
         "fields": [{"regex": r"\d{4}"}],
         "contacts": []}
    ], False),
    ([
        {"name": "invalid_fields_not_list",
         "fields": {"regex": r"\d{4}"},
         "contacts": []}
    ], False),
    ([
        {"name": "invalid_no_fields_regex",
         "fields": [{"field": "test"}],
         "contacts": []}
    ], False),
    ([
        {"name": "invalid_no_fields_regex",
         "fields": [{"field": "tags", "regex": "atag"}],
         "exclude": True,
         "contacts": []}
    ], True),
]


@pytest.mark.parametrize('doc, is_valid', TESTDOCS)
def test_rules_validation(doc, is_valid):
    '''
    Test rule validation
    '''
    res = mailer.validate_rules(doc)
    if is_valid:
        assert res is not None and res == doc
    else:
        assert res is None or res == []


RULES_DATA = [
    # ({'resource': 'server-1234', 'event': '5678'}, [], []),
    ({'resource': '1234', 'event': '5678'},
     [{"name": "Test1",
       "fields": [{"field": "resource", "regex": r"(\w.*)?\d{4}"}],
       "contacts": ["test@example.com"]}],
     ['test@example.com'])
]


@pytest.mark.parametrize('alert_spec, input_rules, expected_contacts',
                         RULES_DATA)
def test_rules_evaluation(alert_spec, input_rules, expected_contacts):
    '''
    Test that rules are properly evaluated
    '''
    with patch.dict(mailer.OPTIONS, mailer.DEFAULT_OPTIONS):
        mailer.OPTIONS['mail_to'] = []
        mailer.OPTIONS['group_rules'] = input_rules
        mail_sender = mailer.MailSender()
        with patch.object(mail_sender, '_send_email_message') as _sem:
            alert = Alert.parse(alert_spec)
            _, emailed_contacts = mail_sender.send_email(alert)
            assert _sem.call_count == 1
            assert emailed_contacts == expected_contacts


def test_rule_matches_list():
    '''
    Test regex matching is working properly
    for a list
    '''
    # Mock options to instantiate mailer
    with patch.dict(mailer.OPTIONS, mailer.DEFAULT_OPTIONS):
        mail_sender = mailer.MailSender()
        with patch.object(mailer, 're') as regex:
            regex.match.side_effect = [MagicMock(), None]
            assert mail_sender._rule_matches('regex', ['item1']) is True
            regex.match.assert_called_with('regex', 'item1')
            assert mail_sender._rule_matches('regex', ['item2']) is False 
            regex.match.assert_called_with('regex', 'item2')


def test_rule_matches_string():
    '''
    Test regex matching is working properly
    for a string
    '''
    # Mock options to instantiate mailer
    with patch.dict(mailer.OPTIONS, mailer.DEFAULT_OPTIONS):
        mail_sender = mailer.MailSender()
        with patch.object(mailer, 're') as regex:
            regex.search.side_effect = [MagicMock(), None]
            assert mail_sender._rule_matches('regex', 'value1') is True
            regex.search.assert_called_with('regex', 'value1')
            assert mail_sender._rule_matches('regex', 'value2') is False
            regex.search.assert_called_with('regex', 'value2')

