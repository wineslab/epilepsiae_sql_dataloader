# Generated by CodiumAI

import pytest
from epilepsiae_sql_dataloader.RelationalRigging.MetaDataBuilder import MetaDataBuilder
from epilepsiae_sql_dataloader.utils import session_scope
from epilepsiae_sql_dataloader.models.Sample import Sample
from pathlib import Path
from datetime import datetime
import pandas as pd
from pandas import DataFrame

# Import the test data which is one in a same level dir called test_data/seizure_data_with_comments.txt
seizure_list_base = Path(__file__).parent / "test_data" / "seizurelists"

good_test_data_path = seizure_list_base / "seizure_data_with_comments.txt"
seizure_data_one_row_path = seizure_list_base / "seizure_data_one_row.txt"
seizure_data_missing_values_path = seizure_list_base / "seizure_data_missing_values.txt"
seizure_data_invalid_datetime_path = (
    seizure_list_base / "seizure_data_invalid_datetime.txt"
)

ENGINE_STR = "postgresql+psycopg2://postgres:postgres@localhost/seizure_db_test"


class TestReadSeizureData:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.meta_data_builder = MetaDataBuilder(
            None
        )  # No need for a session in these tests

    @staticmethod
    def date_time_converter(x):
        return datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

    # Tests that the method reads seizure data from a valid file path
    def test_valid_file_path(self):
        data = self.meta_data_builder.read_seizure_data(good_test_data_path)
        assert len(data) == 5
        assert data[0][0] == self.date_time_converter("2008-11-11 06:10:03.416992")
        assert data[0][1] == self.date_time_converter("2008-11-11 06:10:08.325195")
        assert data[0][2] == 1526187
        assert data[0][3] == 1531213

    # Tests that the method reads seizure data from a file with only one row of data
    def test_file_with_one_row_of_seizure_data(self):
        data = self.meta_data_builder.read_seizure_data(seizure_data_one_row_path)
        assert len(data) == 1
        assert data[0][0] == self.date_time_converter("2008-11-11 06:10:03.416992")
        assert data[0][1] == self.date_time_converter("2008-11-11 06:10:08.325195")
        assert data[0][2] == 1526187
        assert data[0][3] == 1531213

    # Tests that the method handles seizure data with missing values
    def test_file_with_missing_values(self):
        data = self.meta_data_builder.read_seizure_data(
            seizure_data_missing_values_path
        )
        assert len(data) == 2
        assert data[0][0] == self.date_time_converter("2008-11-11 06:10:03.416992")
        assert data[0][1] == self.date_time_converter("2008-11-11 06:10:08.325195")
        assert data[0][2] == 1526187
        assert data[0][3] == 1531213

    # Tests that the method handles seizure data with invalid datetime format
    def test_file_with_invalid_datetime_format(self):
        data = self.meta_data_builder.read_seizure_data(
            seizure_data_invalid_datetime_path
        )
        assert len(data) == 3


class TestReadSampleData:
    base_head_path = Path(__file__).parent / "test_data" / "head_files"
    empty_head = base_head_path / "empty.head"
    missing_fields_head = base_head_path / "missing_fields.head"
    good_head = base_head_path / "good.head"
    invalid_head = base_head_path / "invalid.head"
    mistyped_head = base_head_path / "mistyped.head"

    # Tests that the method can read a valid file path
    def test_valid_file_path(self):
        builder = MetaDataBuilder(None)
        df = builder.read_sample_data(self.good_head)
        assert isinstance(df, DataFrame)

    # Tests that the method can read a file with all fields present and valid
    def test_all_fields_present_and_valid(self):
        builder = MetaDataBuilder(None)
        df = builder.read_sample_data(self.good_head)
        assert df["start_ts"][0] == pd.Timestamp("2008-11-03 20:34:03")
        assert df["num_samples"][0] == 3686400
        assert df["sample_freq"][0] == 1024
        assert df["conversion_factor"][0] == 0.179
        assert df["num_channels"][0] == 93
        assert (
            df["elec_names"][0]
            == "GA1,GA2,GA3,GA4,GA5,GA6,GA7,GA8,GB1,GB2,GB3,GB4,GB5,GB6,GB7,GB8,GC1,GC2,GC3,GC4,GC5,GC6,GC7,GC8,GD1,GD2,GD3,GD4,GD5,GD6,GD7,GD8,GE1,GE2,GE3,GE4,GE5,GE6,GE7,GE8,GF1,GF2,GF3,GF4,GF5,GF6,GF7,GF8,GG1,GG2,GG3,GG4,GG5,GG6,GG7,GG8,GH1,GH2,GH3,GH4,GH5,GH6,GH7,GH8,M1,M2,M3,M4,M5,M6,M7,M8,IHA1,IHA2,IHA3,IHA4,IHB1,IHB2,IHB3,IHB4,IHC1,IHC2,IHC3,IHC4,IHD1,IHD2,IHD3,IHD4,FL1,FL2,FL3,FL4,ECG"
        )
        assert df["pat_id"][0] == 108402
        assert df["adm_id"][0] == 1084102
        assert df["rec_id"][0] == 108400102
        assert df["duration_in_sec"][0] == 3600
        assert df["sample_bytes"][0] == 2

    # Tests that the method can handle a file with no data
    def test_file_with_no_data(self):
        builder = MetaDataBuilder(None)
        df = builder.read_sample_data(self.empty_head)
        assert isinstance(df, DataFrame)
        assert df.empty

    # Tests that the method can handle a file with missing fields
    def test_file_with_missing_fields(self):
        builder = MetaDataBuilder(None)
        df = builder.read_sample_data(self.missing_fields_head)
        assert isinstance(df, DataFrame)
        assert df.empty

    # Tests that the method can handle a file with invalid data
    def test_file_with_invalid_data(self):
        builder = MetaDataBuilder(None)
        fp = Path(self.invalid_head)
        df = builder.read_sample_data(fp)
        assert isinstance(df, DataFrame)
        assert df.empty

    # Tests that the method can handle a file with non-numeric values in numeric fields
    def test_non_numeric_values_in_numeric_fields(self):
        builder = MetaDataBuilder(None)
        df = builder.read_sample_data(self.mistyped_head)
        assert isinstance(df, DataFrame)
        assert df.empty


class TestFileGenerator:
    # Tests that the method returns a generator when a valid directory path is passed as input
    def test_valid_directory_path(self):
        builder = MetaDataBuilder(ENGINE_STR)
        directory = Path("tests/test_data/file_generator_test")
        assert len(list(builder.file_generator(directory))) == 1

    # Tests that the method returns an empty generator when an empty directory is passed as input
    def test_empty_directory(self):
        builder = MetaDataBuilder(ENGINE_STR)
        directory = Path("tests/test_data/file_generator_test/empty")
        assert len(list(builder.file_generator(directory))) == 0

    # Tests that the method returns an empty generator when the rec_* directories do not contain any *.head files
    def test_no_head_files(self):
        builder = MetaDataBuilder(ENGINE_STR)
        directory = Path("tests/test_data/seizurelists")
        assert len(list(builder.file_generator(directory))) == 0
