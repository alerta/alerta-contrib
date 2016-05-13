'''
Unit test definitions for all rules
'''
import pytest
import mailer
from mock import MagicMock, patch, DEFAULT


def test_rules_dont_exist():
    '''
    Test the rules file is read
    '''
    with patch('mailer.os') as system_os:
        system_os.path.exists.return_value = False
        res = mailer.parse_group_rules('config_file')
        system_os.path.exists.called_once_with('confile_file')
        assert res is None


def test_rules_parsing():
    '''
    Test the rules file is properly read
    '''
    with patch.multiple(mailer, os=DEFAULT, open=DEFAULT,
                        json=DEFAULT, validate_rules=DEFAULT) as mocks:
        mocks['os'].path.exists.return_value = True
        mocks['os'].walk().__iter__\
            .return_value = [(None, None, 'cantopen.json'),
                             (None, None, 'invalid.json'),
                             (None, None, 'valid.json')]
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
        {"name": "invalid_no_fields"}
    ], False),
    ([
        {"name": "invalid_empty_fields",
         "fields": []}
    ], False),
    ([
        {"name": "invalid_no_contacts",
         "fields": [{"field": "resource", "regex": r"\d{4}"}]}
    ], False),
    ([
        {"name": "invalid_no_fields_field",
         "fields": [{"regex": r"\d{4}"}]}
    ], False),
    ([
        {"name": "invalid_no_fields_not_list",
         "fields": {"regex": r"\d{4}"}}
    ], False),
    ([
        {"name": "invalid_no_fields_regex",
         "fields": [{"field": "test"}]}
    ], False),
]


@pytest.mark.parametrize('doc, is_valid', TESTDOCS)
def test_rules_validation(doc, is_valid):
    '''
    Test rule validation
    '''
    res = mailer.validate_rules(doc)
    if is_valid:
        assert res is not None
    else:
        assert res is None or res == []


RULES_DATA = [
    [],
    [{
        "name": "Test1",
        "fields": [{"field": "resource", "regex": r"\d{4}"}],
        "contacts": ["test@example.com"]
    }]
]


@pytest.mark.parametrize('rules', RULES_DATA)
def test_rules_evaluation(rules):
    '''
    Test that rules are properly evaluated
    '''
    with patch.dict(mailer.OPTIONS, mailer.DEFAULT_OPTIONS):
        contacts = MagicMock()
        mailer.OPTIONS['mail_to'] = contacts
        print contacts, list(contacts)
        mailer.OPTIONS['group_rules'] = rules
        mail_sender = mailer.MailSender()
        with patch.object(mail_sender, '_send_email_message') as _sem:
            with patch.object(mailer, 're') as regex:
                alert = MagicMock()
                mail_sender.send_email(alert)
                assert _sem.call_count == 1
                call_count = 0
                for rule in rules:
                    contacts.extend.assert_called_once_with(rule['contacts'])
                    call_count += len(rule['fields'])
                    for fields in rule['fields']:
                        regex.match.assert_called_with(
                            fields['regex'],
                            getattr(alert, fields['field']))
                assert regex.match.call_count == call_count
