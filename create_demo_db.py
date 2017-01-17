from badmin_api import app
import db_helper
import user_model
import club_model
import practice_model
import dateutil.parser

with app.app_context():
    db_helper.db.create_all()

    test_user_1 = user_model.User('Anders And', 'anders@andebymail.com', '12345678')
    test_user_2 = user_model.User('Andersine And', 'andersine@andebymail.com', '12345678')
    test_user_3 = user_model.User('Joakim von And', 'joakim@andebymail.com', '12345678')
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

    test_club_2 = club_model.Club('Von And Badmintonklub', [test_user_3])
    test_club_2.members.append(test_user_2)
    test_club_2.coaches.append(test_user_2)
    db_helper.db.session.add(test_club_2)
    db_helper.db.session.commit()

    test_practice_1 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-01T12:00:00'), 120)
    test_practice_1.invited.append(test_user_1)
    test_practice_1.confirmed.append(test_user_2)

    test_practice_2 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-03T12:00:00'), 120)
    test_practice_2.invited.append(test_user_2)
    test_practice_2.declined.append(test_user_1)

    test_practice_3 = practice_model.Practice('A-træning', test_club_1, dateutil.parser.parse('2017-01-05T12:00:00'), 120)
    test_practice_3.invited.append(test_user_1)
    test_practice_3.invited.append(test_user_2)

    db_helper.db.session.add(test_practice_1)
    db_helper.db.session.commit()
    db_helper.db.session.add(test_practice_2)
    db_helper.db.session.commit()
    db_helper.db.session.add(test_practice_3)
    db_helper.db.session.commit()