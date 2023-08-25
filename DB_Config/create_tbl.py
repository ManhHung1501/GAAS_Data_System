import mysql.connector
from credential import mysql_dw

# Create paritition by day script
partition_template = ", ".join([f"PARTITION p{i} VALUES LESS THAN ({i+1})" for i in range(1, 91)])

# action
script = """create table actions
(
    action_id           varchar(255) charset utf8             not null,
    partition_id        int                                   not null,
    user_id             varchar(255) charset utf8             not null,
    binding_token       varchar(255) charset utf8             null,
    action_name         varchar(255) charset utf8             null,
    action_date         date                                  null,
    client_time         datetime(3)                           null,
    game_time           datetime(3)                           null,
    server_time         datetime(3)                           null,
    parameters          mediumtext                            null,
    current_sequence    int                                   null,
    session_number      int                                   null,
    client_version      int                                   null,
    check_point         int                                   null,
    reason_ban          text                                  null,
    inserted_time       timestamp default current_timestamp() not null,
    unique key action_id (action_id, partition_id)
)
partition by range(partition_id) ({});

create index idx_user_id
    on actions (user_id);
create index idx_user_id_token
    on actions (user_id, binding_token);
create index idx_action_name
    on actions (action_name);
create index idx_action_date_name
    on actions (action_date, action_name);

create table transactions
(
    transaction_id      varchar(255) charset utf8             not null,
    partition_id        int                                   not null,
    user_id             varchar(255) charset utf8             not null,
    binding_token       varchar(255) charset utf8             null,
    source_id           int                                   null,
    transaction_name    varchar(255) charset utf8             null,
    transaction_date    date                                  null,
    amount              int                                   null,
    client_time         datetime(3)                           null,
    game_time           datetime(3)                           null,
    server_time         datetime(3)                           null,
    parameters          mediumtext                            null,
    current_sequence    int                                   null,
    session_number      int                                   null,
    client_version      int                                   null,
    check_point         int                                   null,
    reason_ban          text                                  null,
    inserted_time       timestamp default current_timestamp() not null,
    unique key transaction_id (transaction_id, partition_id)
)
partition by range(partition_id) ({});

create index idx_user_id
    on transactions (user_id);
create index idx_user_id_token
    on transactions (user_id, binding_token);
create index idx_transaction_name
    on transactions (transaction_name);
create index idx_transaction_date_name
    on transactions (transaction_date, transaction_name);

create table users
(
    user_id             varchar(255) charset UTF8             not null
        primary key,
    country_code        varchar(10) charset utf8              null,
    campaign_level      int                                   null,
    device_type         varchar(10) charset utf8              null,
    last_online_time    datetime(3)                           null,
    gold                int                                   null,
    crystal             int                                   null,
    piece               int                                   null,
    vip_point           int                                   null,
    user_resource       text                                  null,
    total_star          int                                   null,
    total_camp_star     int                                   null,
    total_ship_star     int                                   null,
    total_skinlv_star   int                                   null,
    total_drone_star    int                                   null,
    hero_level_star     int                                   null,
    miniboss_level_star int                                   null,
    campaign_star       text                                  null,
    ship_skinlv_star    text                                  null,
    drone_level_star    text                                  null,
    ship_level_star     text                                  null,
    change_local_time   varchar(10) charset utf8              null,
    creation_time       datetime(3)                           null,
    creation_date       date                                  null,
    app_version         varchar(50) charset utf8              null,
    client_version      int                                   null,
    inserted_time       timestamp default current_timestamp() not null,
    modified_time       timestamp default current_timestamp() not null on update current_timestamp()
);

create table space_ships
(
    user_id          varchar(255) charset utf8             not null,
    ship_index       int                                   not null,
    bullet_level     int                                   null,
    power_level      int                                   null,
    evolve_level     int                                   null,
    experience_point decimal                               null,
    skin             text                                  null,
    inserted_time    timestamp default current_timestamp() not null,
    modified_time    timestamp default current_timestamp() not null on update current_timestamp(),
    primary key (user_id, ship_index),
    constraint unique_user_index
        unique (user_id, ship_index)
);

create table drones
(
    user_id       varchar(255) charset utf8             not null,
    drone_index   int                                   not null,
    power_level   int                                   null,
    skin          text                                  null,
    inserted_time timestamp default current_timestamp() not null,
    modified_time timestamp default current_timestamp() not null on update current_timestamp(),
    primary key (user_id, drone_index),
    constraint unique_user_index
        unique (user_id, drone_index)
);

create table pilots
(
    user_id       varchar(255) charset utf8             not null,
    pilot_id      int                                   not null,
    pilot_level   int                                   null,
    inserted_time timestamp default current_timestamp() not null,
    modified_time timestamp default current_timestamp() not null on update current_timestamp(),
    primary key (user_id, pilot_id),
    constraint unique_user_index
        unique (user_id, pilot_id)
);

create table talents
(
    user_id       varchar(255) charset utf8             not null,
    talent_id     int                                   not null,
    talent_level  int                                   null,
    inserted_time timestamp default current_timestamp() not null,
    modified_time timestamp default current_timestamp() not null on update current_timestamp(),
    primary key (user_id, talent_id),
    constraint unique_user_index
        unique (user_id, talent_id)
);

create table expert_items
(
    user_id           varchar(255) charset utf8             not null,
    expert_item_id    int                                   not null,
    expert_item_level int                                   null,
    equipping_ship    int                                   null,
    slot_equipped     int                                   null,
    inserted_time     timestamp default current_timestamp() not null,
    modified_time     timestamp default current_timestamp() not null on update current_timestamp(),
    primary key (user_id, expert_item_id),
    constraint unique_user_index
        unique (user_id, expert_item_id)
);
""".format(partition_template, partition_template)

# Connect to MySQL
try:
    cnx = mysql.connector.connect(**mysql_dw)
    mysql_cursor = cnx.cursor()
    print("Connected to the database.")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Error: Access denied. Check your username and password.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Error: The specified database does not exist.")
    else:
        print("Error: {}".format(err))
    exit(1)

mysql_cursor.execute(script)

