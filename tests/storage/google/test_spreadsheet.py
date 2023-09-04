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
        values = [1, 2, 3]

        worksheet = Worksheet("worksheet", spreadsheet=spreadsheet_mock)
        worksheet.insert(values)

        insert_mock = spreadsheet_mock.worksheet_by_title.return_value.insert_rows
        insert_mock.assert_called_once_with(1, number=len(values), values=values)

    def test_get_values(self, mocker):
        spreadsheet_mock = mocker.MagicMock()

        worksheet = Worksheet("worksheet", spreadsheet=spreadsheet_mock)
        rows = worksheet.get_all()

        get_values_mock = spreadsheet_mock.worksheet_by_title.return_value.get_values
        get_values_mock.assert_called_once_with(None, None)
        assert rows == get_values_mock.return_value

    def test_get_values_cast(self, mocker):
        spreadsheet_mock = mocker.MagicMock()
        get_values_mock = spreadsheet_mock.worksheet_by_title.return_value.get_values
        get_values_mock.return_value = [[1, 2, 3], [1, 4, 6]]

        worksheet = Worksheet("worksheet", spreadsheet=spreadsheet_mock)
        rows = worksheet.get_all(cast=tuple)

        assert rows == [(1, 2, 3), (1, 4, 6)]

    def test_deduplicated(self, mocker):
        def deduplicate(rows, existing_rows):
            return [r for r in rows if r not in existing_rows]

        spreadsheet_mock = mocker.MagicMock()
        get_values_mock = spreadsheet_mock.worksheet_by_title.return_value.get_values
        get_values_mock.return_value = [["row 1"], ["row 2"]]
        values = [["row 1"], ["not duplicated row"]]

        worksheet = Worksheet("worksheet", spreadsheet=spreadsheet_mock)
        deduplicated_rows = worksheet.deduplicate(values, deduplicate)

        assert deduplicated_rows == [["not duplicated row"]]

    def test_insert_deduplicate(self, mocker):
        def deduplicate(rows, existing_rows):
            return [r for r in rows if r not in existing_rows]

        spreadsheet_mock = mocker.MagicMock()
        get_values_mock = spreadsheet_mock.worksheet_by_title.return_value.get_values
        get_values_mock.return_value = [["row 1"], ["row 2"]]
        values = [["row 1"], ["not duplicated row"]]

        worksheet = Worksheet("worksheet", spreadsheet=spreadsheet_mock)
        worksheet.insert(values, deduplicate=deduplicate)

        expected_values = [["not duplicated row"]]
        insert_mock = spreadsheet_mock.worksheet_by_title.return_value.insert_rows
        insert_mock.assert_called_once_with(
            1, number=len(expected_values), values=expected_values
        )
