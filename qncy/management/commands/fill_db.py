from django.core.management.base import BaseCommand
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
                email=fake.email(),
                username=fake.user_name() + str(randint(1, 71)),
            )
            user.set_password("demopassword")
            users.append(user)

            # We can't ignore_conflicts like with votes because that prevents
            # us from getting primary keys, making tagging impossible
            try:
                tag_name = " ".join(fake.words(randint(1, 3)))
                tag = Tag(name=tag_name)
                tag.save()
                tags.append(tag)
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING('Skipped tag due to constraint ("%s")' % tag)
                )
        users = User.objects.bulk_create(users, batch_size=50)
        self.stdout.write(self.style.SUCCESS(f"Created {options['ratio'][0]} users"))

        for _ in range(options["ratio"][0] * 10):
            question = Question(
                author=choice(users),
                title=fake.sentence(),
                content=fake.text(),
            )
            questions.append(question)
        questions = Question.objects.bulk_create(questions, batch_size=200)
        self.stdout.write(
            self.style.SUCCESS(f"Created {options['ratio'][0] * 10} questions")
        )

        for _ in range(options["ratio"][0] * 100):
            answer = Answer(
                question=choice(questions),
                author=choice(users),
                content=fake.paragraph(),
            )
            answers.append(answer)
        answers = Answer.objects.bulk_create(answers, batch_size=200)
        self.stdout.write(
            self.style.SUCCESS(f"Created {options['ratio'][0] * 100} answers")
        )

        answer_votes = []
        question_votes = []
        for _ in range(options["ratio"][0] * 200):
            if choice([True, False]):
                av = AnswerVote(
                    answer=choice(answers),
                    user=choice(users),
                    up=(randint(1, 5) > 1),
                )
                answer_votes.append(av)
            else:
                qv = QuestionVote(
                    question=choice(questions),
                    user=choice(users),
                    up=(randint(1, 5) > 1),
                )
                question_votes.append(qv)
        AnswerVote.objects.bulk_create(
            answer_votes, ignore_conflicts=True, batch_size=1000
        )
        QuestionVote.objects.bulk_create(
            question_votes, ignore_conflicts=True, batch_size=1000
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {options['ratio'][0] * 200} votes")
        )

        for question in questions:
            question.tags.set(choices(tags, k=randint(1, 4)))
            question.update_rating()
        for answer in answers:
            answer.update_rating()
        self.stdout.write(
            self.style.SUCCESS("Tagged and rated all questions and answers")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully filled db with ratio of {options['ratio'][0]}"
            )
        )
