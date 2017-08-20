from badmin_api import app
import db_helper
import user_model
import club_model
import practice_model
import decline_notice_model
import confirm_notice_model
import dateutil.parser

"""
Clear postgres db
DROP SCHEMA public CASCADE;CREATE SCHEMA public;GRANT ALL ON SCHEMA public TO postgres;GRANT ALL ON SCHEMA public TO public;COMMENT ON SCHEMA public IS 'standard public schema';
"""


with app.app_context():
    db_helper.db.create_all()

    test_user_1 = user_model.User('Anders And', 'anders', '12345678', 'foobar')
    test_user_2 = user_model.User('Andersine And', 'andersine@andebymail.com', '12345678', 'foobar')
    test_user_3 = user_model.User('Joakim von And', 'joakim@andebymail.com', '12345678', 'foobar')
    db_helper.db.session.add(test_user_1)
    db_helper.db.session.add(test_user_2)
    db_helper.db.session.add(test_user_3)
    db_helper.db.session.commit()

    test_club_1 = club_model.Club('Andeby Badmintonklub', [test_user_1])
    test_club_1.members.append(test_user_1)
    test_club_1.members.append(test_user_2)
    test_club_1.coaches.append(test_user_1)
    test_club_1.membershipRequests.append(test_user_3)
    db_helper.db.session.add(test_club_1)
    db_helper.db.session.commit()

    test_practice_1 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-08-20T12:00:00'), 120)
    test_practice_1.invited.append(test_user_1)
    cn1 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_1.confirmed.append(cn1)
    test_user_2.confirmedPractices.append(cn1)

    test_practice_2 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-08-22T12:00:00'), 120)
    test_practice_2.invited.append(test_user_2)
    dn1 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_2.declined.append(dn1)
    test_user_1.declinedPractices.append(dn1)

    test_practice_3 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-08-23T12:00:00'), 120)
    test_practice_3.invited.append(test_user_1)
    test_practice_3.invited.append(test_user_2)

    # Test data for week view table
    test_practice_4 = practice_model.Practice('A-træning (Mandag)', test_club_1, dateutil.parser.parse('2017-08-25T12:00:00'), 120)
    cn2 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_4.confirmed.append(cn2)
    test_user_1.confirmedPractices.append(cn2)
    cn3 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_4.confirmed.append(cn3)
    test_user_2.confirmedPractices.append(cn3)
    cn4 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_4.confirmed.append(cn4)
    test_user_3.confirmedPractices.append(cn4)

    test_practice_5 = practice_model.Practice('B-træning (Tirsdag)', test_club_1, dateutil.parser.parse('2017-08-27T12:00:00'), 120)
    test_practice_5.invited.append(test_user_1)
    test_practice_5.invited.append(test_user_2)
    test_practice_5.invited.append(test_user_3)

    test_practice_7 = practice_model.Practice('Fysisk (Onsdag)', test_club_1, dateutil.parser.parse('2017-08-29T08:00:00'), 120)
    cn5 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_7.confirmed.append(cn5)
    test_user_2.confirmedPractices.append(cn5)
    cn6 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_7.confirmed.append(cn6)
    test_user_2.confirmedPractices.append(cn6)

    test_practice_6 = practice_model.Practice('A-træning (Onsdag)', test_club_1, dateutil.parser.parse('2017-09-01T12:00:00'), 120)
    test_practice_6.invited.append(test_user_1)
    cn7 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_6.confirmed.append(cn7)
    test_user_2.confirmedPractices.append(cn7)    
    dn2 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_6.declined.append(dn2)
    test_user_3.declinedPractices.append(dn2)

    test_practice_8 = practice_model.Practice('B-træning (Torsdag)', test_club_1, dateutil.parser.parse('2017-09-03T12:00:00'), 120)
    dn3 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_8.declined.append(dn3)
    test_user_1.declinedPractices.append(dn3)
    cn8 = confirm_notice_model.ConfirmNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_8.confirmed.append(cn8)
    test_user_2.confirmedPractices.append(cn8)   
    test_practice_8.invited.append(test_user_3)

    test_practice_9 = practice_model.Practice('Fysisk (Fredag)', test_club_1, dateutil.parser.parse('2017-09-05T12:00:00'), 120)
    dn4 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_9.declined.append(dn4)
    test_user_1.declinedPractices.append(dn4)
    dn5 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_9.declined.append(dn5)
    test_user_2.declinedPractices.append(dn5)
    dn6 = decline_notice_model.DeclineNotice(dateutil.parser.parse('2017-07-03T12:00:00'))
    test_practice_9.declined.append(dn6)
    test_user_3.declinedPractices.append(dn6)

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
    db_helper.db.session.add(dn1)
    db_helper.db.session.add(dn2)
    db_helper.db.session.add(dn3)
    db_helper.db.session.add(dn4)
    db_helper.db.session.add(dn5)
    db_helper.db.session.add(dn6)
    db_helper.db.session.add(cn1)
    db_helper.db.session.add(cn2)
    db_helper.db.session.add(cn3)
    db_helper.db.session.add(cn4)
    db_helper.db.session.add(cn5)
    db_helper.db.session.add(cn6)
    db_helper.db.session.add(cn7)
    db_helper.db.session.add(cn8)


    db_helper.db.session.commit()