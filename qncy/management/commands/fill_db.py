from django.core.management.base import BaseCommand, CommandError
from qncy.models import Question, User, Tag, Answer, AnswerVote, QuestionVote
from django.db import IntegrityError

from random import choice, choices, randint

from faker import Faker

class Command(BaseCommand):
    help = "Fills the database with mock data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", nargs=1, type=int)

    def handle(self, *args, **options):
        fake = Faker()

        # <ratio> users
        # <ratio>*10 questions
        # <ratio>*100 answers
        # <ratio> tags
        # <ratio>*200 votes

        users = []
        tags = []
        questions = []
        answers = []

        for _ in range(options["ratio"][0]):
            user = User(
                email = fake.email(),
                username=fake.user_name(),
            )
            user.set_password("demopassword")
            user.save()
            users.append(user)

            try:
                tag = Tag(name=' '.join(fake.words(randint(1, 3))))
                tag.save()
                tags.append(tag)
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING('Skipped tag due to constraint("%s")' % tag)
                )
        
        for _ in range(options["ratio"][0]*10):
            question = Question(
                author=choice(users),
                title=fake.sentence(),
                content=fake.text(),
            )
            question.save()
            question.tags.set(choices(tags, k=randint(1,4)))
            question.save()
            questions.append(question)
        for _ in range(options["ratio"][0]*100):
            answer = Answer(
                question=choice(questions),
                author=choice(users),
                content=fake.paragraph(),
            )
            answer.save()
            answers.append(answer)
        
        for _ in range(options["ratio"][0]*200):
            # we are poised to run into a couple integrity errors
            # this is a hack, true.
            if choice([True, False]):
                while True:
                    try:
                        av = AnswerVote(
                            answer=choice(answers),
                            user=choice(users),
                            up=(randint(1,5) > 1),
                        )
                        av.save()
                        av.answer.update_rating()
                        break
                    except IntegrityError:
                        continue
            else:
               while True:
                    try:
                        qv = QuestionVote(
                            question=choice(questions),
                            user=choice(users),
                            up=(randint(1,5) > 1),
                        )
                        qv.save()
                        qv.question.update_rating()
                        break
                    except IntegrityError:
                        continue 

        self.stdout.write(
            self.style.SUCCESS('Successfully filled db "%s"' % options["ratio"])
        )
