import pytest
from copy import deepcopy

from dlt.common.utils import uniq_id, custom_environ
from dlt.common.schema import Schema
from dlt.common.configuration import resolve_configuration
from dlt.common.configuration.specs import PostgresCredentials

from dlt.destinations.exceptions import DestinationSchemaWillNotUpdate
from dlt.destinations.redshift.redshift import RedshiftClient
from dlt.destinations.redshift.configuration import RedshiftClientConfiguration

from tests.load.utils import TABLE_UPDATE


@pytest.fixture
def schema() -> Schema:
    return Schema("event")


@pytest.fixture
def client(schema: Schema) -> RedshiftClient:
    # return client without opening connection
    return RedshiftClient(schema, RedshiftClientConfiguration(dataset_name="test_" + uniq_id()))


def test_configuration() -> None:
    # check names normalized
    with custom_environ({"DESTINATION__REDSHIFT__CREDENTIALS__DATABASE": "UPPER_CASE_DATABASE", "DESTINATION__REDSHIFT__CREDENTIALS__PASSWORD": " pass\n"}):
        C = resolve_configuration(PostgresCredentials(), namespaces=("destination", "redshift"))
        assert C.database == "upper_case_database"
        assert C.password == "pass"


def test_create_table(client: RedshiftClient) -> None:
    # non existing table
    sql = client._get_table_update_sql("event_test_table", TABLE_UPDATE, False)
    assert "event_test_table" in sql
    assert '"col1" bigint  NOT NULL' in sql
    assert '"col2" double precision  NOT NULL' in sql
    assert '"col3" boolean  NOT NULL' in sql
    assert '"col4" timestamp with time zone  NOT NULL' in sql
    assert '"col5" varchar(max)' in sql
    assert '"col6" numeric(38,9)  NOT NULL' in sql
    assert '"col7" varbinary' in sql
    assert '"col8" numeric(38,0)' in sql
    assert '"col9" super  NOT NULL' in sql


def test_alter_table(client: RedshiftClient) -> None:
    # existing table has no columns
    sql = client._get_table_update_sql("event_test_table", TABLE_UPDATE, True)
    canonical_name = client.sql_client.make_qualified_table_name("event_test_table")
    # must have several ALTER TABLE statements
    assert sql.count(f"ALTER TABLE {canonical_name}\nADD COLUMN") == len(TABLE_UPDATE)
    assert "event_test_table" in sql
    assert '"col1" bigint  NOT NULL' in sql
    assert '"col2" double precision  NOT NULL' in sql
    assert '"col3" boolean  NOT NULL' in sql
    assert '"col4" timestamp with time zone  NOT NULL' in sql
    assert '"col5" varchar(max)' in sql
    assert '"col6" numeric(38,9)  NOT NULL' in sql
    assert '"col7" varbinary' in sql
    assert '"col8" numeric(38,0)' in sql
    assert '"col9" super  NOT NULL' in sql


def test_create_table_with_hints(client: RedshiftClient) -> None:
    mod_update = deepcopy(TABLE_UPDATE)
    # timestamp
    mod_update[0]["primary_key"] = True
    mod_update[0]["sort"] = True
    mod_update[1]["cluster"] = True
    mod_update[4]["cluster"] = True
    sql = client._get_table_update_sql("event_test_table", mod_update, False)
    # PRIMARY KEY will not be present https://heap.io/blog/redshift-pitfalls-avoid
    assert '"col1" bigint SORTKEY NOT NULL' in sql
    assert '"col2" double precision DISTKEY NOT NULL' in sql
    assert '"col5" varchar(max) DISTKEY' in sql
    # no hints
    assert '"col3" boolean  NOT NULL' in sql
    assert '"col4" timestamp with time zone  NOT NULL' in sql


def test_hint_alter_table_exception(client: RedshiftClient) -> None:
    mod_update = deepcopy(TABLE_UPDATE)
    # timestamp
    mod_update[3]["sort"] = True
    with pytest.raises(DestinationSchemaWillNotUpdate) as excc:
        client._get_table_update_sql("event_test_table", mod_update, True)
    assert excc.value.columns == ['"col4"']
