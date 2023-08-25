action = """
insert into actions 
    (action_id, partition_id, user_id, binding_token, action_name, action_date, client_time, game_time,
    server_time, parameters, current_sequence, session_number, client_version, check_point, reason_ban)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

transaction = """
insert into transactions 
    (transaction_id, partition_id, user_id, binding_token, source_id, transaction_name,
    transaction_date, amount, client_time, game_time, server_time, parameters, current_sequence,
    session_number, client_version, check_point, reason_ban)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

user ="""
insert into users 
    (user_id, country_code, campaign_level, device_type, last_online_time, gold,
    crystal, piece, vip_point, user_resource, total_star, total_camp_star,
    total_ship_star, total_skinlv_star, total_drone_star, hero_level_star,
    miniboss_level_star, campaign_star, ship_skinlv_star, drone_level_star,
    ship_level_star, change_local_time, creation_time, creation_date, app_version,
    client_version)
values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    country_code = VALUES(country_code),
    campaign_level = VALUES(campaign_level),
    device_type = VALUES(device_type),
    last_online_time = VALUES(last_online_time),
    gold = VALUES(gold),
    crystal = VALUES(crystal),
    piece = VALUES(piece),
    vip_point = VALUES(vip_point),
    user_resource = VALUES(user_resource),
    total_star = VALUES(total_star),
    total_camp_star = VALUES(total_camp_star),
    total_ship_star = VALUES(total_ship_star),
    total_skinlv_star = VALUES(total_skinlv_star),
    total_drone_star = VALUES(total_drone_star),
    hero_level_star = VALUES(hero_level_star),
    miniboss_level_star = VALUES(miniboss_level_star),
    campaign_star = VALUES(campaign_star),
    ship_skinlv_star = VALUES(ship_skinlv_star),
    drone_level_star = VALUES(drone_level_star),
    ship_level_star = VALUES(ship_level_star),
    change_local_time = VALUES(change_local_time),
    creation_time = VALUES(creation_time),
    creation_date = VALUES(creation_date),
    app_version = VALUES(app_version),
    client_version = VALUES(client_version);
"""

sl = """
INSERT INTO space_ships (user_id, ship_index, bullet_level, power_level, evolve_level, experience_point, skin)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    bullet_level = VALUES(bullet_level),
    power_level = VALUES(power_level),
    evolve_level = VALUES(evolve_level),
    experience_point = VALUES(experience_point),
    skin = VALUES(skin);
"""

dl = """
INSERT INTO drones 
    (user_id, drone_index, power_level, skin)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    power_level = VALUES(power_level),
    skin = VALUES(skin);
"""

pl = """
INSERT INTO pilots 
    (user_id, pilot_id, pilot_level)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    pilot_level = VALUES(pilot_level);
"""

tl = """
INSERT INTO talents 
    (user_id, talent_id, talent_level)
VALUES (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    talent_level = VALUES(talent_level);
"""

xl = """
INSERT INTO expert_items 
    (user_id, expert_item_id, expert_item_level, equipping_ship, slot_equipped)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    expert_item_level = VALUES(expert_item_level),
    equipping_ship = VALUES(equipping_ship),
    slot_equipped = VALUES(slot_equipped);
"""