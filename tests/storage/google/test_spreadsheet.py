from cronjobs.storage.google.sheet import Spreadsheet, Worksheet


class TestSpreadsheet:
    def test_init(self, mocker):
        client_mock = mocker.MagicMock()
        name = "spreadsheet"

        spreadsheet = Spreadsheet(name, client=client_mock)

        assert spreadsheet.name == name
        assert spreadsheet.client == client_mock
        assert spreadsheet.spreadsheet == client_mock.open(name)

    def test_worksheet_by_title(self, mocker):
        client_mock = mocker.MagicMock()
        spreadsheet_name, worksheet_name = "spreadsheet", "worksheet"

        spreadsheet = Spreadsheet(spreadsheet_name, client=client_mock)
        worksheet = spreadsheet.worksheet_by_title(worksheet_name)

        worksheet_by_title_mock = client_mock.open.return_value.worksheet_by_title
        worksheet_by_title_mock.assert_called_once_with(worksheet_name)
        assert worksheet == worksheet_by_title_mock.return_value


class TestWorksheet:
    def test_init(self, mocker):
        spreadsheet_mock = mocker.MagicMock()
        name = "worksheet"

        worksheet = Worksheet(name, spreadsheet=spreadsheet_mock)

        assert worksheet.spreadsheet == spreadsheet_mock
        worksheet_by_title_mock = spreadsheet_mock.worksheet_by_title
        worksheet_by_title_mock.assert_called_once_with(name)
        assert worksheet.worksheet == worksheet_by_title_mock.return_value

    def test_insert(self, mocker):
        spreadsheet_mock = mocker.MagicMock()
        name = "worksheet"
        values = [1, 2, 3]

        worksheet = Worksheet(name, spreadsheet=spreadsheet_mock)
        worksheet.insert(values)

        insert_mock = spreadsheet_mock.worksheet_by_title.return_value.insert_rows
        insert_mock.assert_called_once_with(1, number=len(values), values=values)
