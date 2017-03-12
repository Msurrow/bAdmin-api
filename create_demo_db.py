from badmin_api import app
import db_helper
import user_model
import club_model
import practice_model
import dateutil.parser

"""
Clear postgres db
DROP SCHEMA public CASCADE;CREATE SCHEMA public;GRANT ALL ON SCHEMA public TO postgres;GRANT ALL ON SCHEMA public TO public;COMMENT ON SCHEMA public IS 'standard public schema';
"""


with app.app_context():
    db_helper.db.create_all()

    test_user_1 = user_model.User('Anders And', 'anders@andebymail.com', '12345678', 'foobar')
    test_user_2 = user_model.User('Andersine And', 'andersine@andebymail.com', '12345678', 'foobar')
    test_user_3 = user_model.User('Joakim von And', 'joakim@andebymail.com', '12345678', 'foobar')
    db_helper.db.session.add(test_user_1)
    db_helper.db.session.add(test_user_2)
    db_helper.db.session.add(test_user_3)
    db_helper.db.session.commit()

    test_club_1 = club_model.Club('Andeby Badmintonklub', [test_user_1])
    test_club_1.members.append(test_user_1)
    test_club_1.members.append(test_user_2)
    test_club_1.coaches.append(test_user_2)
    test_club_1.membershipRequests.append(test_user_3)
    db_helper.db.session.add(test_club_1)
    db_helper.db.session.commit()

    # test_club_2 = club_model.Club('Von And Badmintonklub', [test_user_3])
    # test_club_2.members.append(test_user_2)
    # test_club_2.coaches.append(test_user_2)
    # db_helper.db.session.add(test_club_2)
    # db_helper.db.session.commit()

    test_practice_1 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-01T12:00:00+01:00'), 120)
    test_practice_1.invited.append(test_user_1)
    test_practice_1.confirmed.append(test_user_2)

    test_practice_2 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-03T12:00:00+01:00'), 120)
    test_practice_2.invited.append(test_user_2)
    test_practice_2.declined.append(test_user_1)

    test_practice_3 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-05T12:00:00+01:00'), 120)
    test_practice_3.invited.append(test_user_1)
    test_practice_3.invited.append(test_user_2)

    # Test data for week view table
    test_practice_4 = practice_model.Practice('A-træning (Mandag)', test_club_1, dateutil.parser.parse('2017-01-09T12:00:00+01:00'), 120)
    test_practice_4.confirmed.append(test_user_1)
    test_practice_4.confirmed.append(test_user_2)
    test_practice_4.confirmed.append(test_user_3)
    test_practice_5 = practice_model.Practice('B-træning (Tirsdag)', test_club_1, dateutil.parser.parse('2017-01-10T12:00:00+01:00'), 120)
    test_practice_5.invited.append(test_user_1)
    test_practice_5.invited.append(test_user_2)
    test_practice_5.invited.append(test_user_3)
    test_practice_7 = practice_model.Practice('Fysisk (Onsdag)', test_club_1, dateutil.parser.parse('2017-01-11T08:00:00+01:00'), 120)
    test_practice_7.confirmed.append(test_user_1)
    test_practice_7.confirmed.append(test_user_2)
    test_practice_6 = practice_model.Practice('A-træning (Onsdag)', test_club_1, dateutil.parser.parse('2017-01-11T12:00:00+01:00'), 120)
    test_practice_6.invited.append(test_user_1)
    test_practice_6.confirmed.append(test_user_2)
    test_practice_6.declined.append(test_user_3)
    test_practice_8 = practice_model.Practice('B-træning (Torsdag)', test_club_1, dateutil.parser.parse('2017-01-12T12:00:00+01:00'), 120)
    test_practice_8.declined.append(test_user_1)
    test_practice_8.confirmed.append(test_user_2)
    test_practice_8.invited.append(test_user_3)
    test_practice_9 = practice_model.Practice('Fysisk (Fredag)', test_club_1, dateutil.parser.parse('2017-01-13T12:00:00+01:00'), 120)
    test_practice_9.declined.append(test_user_1)
    test_practice_9.declined.append(test_user_2)
    test_practice_9.declined.append(test_user_3)

    # Commit stuff
    db_helper.db.session.add(test_practice_1)
    db_helper.db.session.add(test_practice_2)
    db_helper.db.session.add(test_practice_3)
    db_helper.db.session.add(test_practice_4)
    db_helper.db.session.add(test_practice_5)
    db_helper.db.session.add(test_practice_6)
    db_helper.db.session.add(test_practice_7)
    db_helper.db.session.add(test_practice_8)
    db_helper.db.session.add(test_practice_9)
  
    db_helper.db.session.commit()