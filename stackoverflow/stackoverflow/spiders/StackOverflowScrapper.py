import urllib
import scrapy
from cssselect import Selector
from stackoverflow.items import StackOverflow


class Stack(scrapy.Spider):
    name = "Stack"
    start_urls = ["https://stackoverflow.com/questions/tagged/"]

    def __init__(self, domain='', *args, **kwargs):
        if domain is not None:
            self.start_urls[0] = self.start_urls[0] + domain
        else:
            self.start_urls = []
        super(Stack, self).__init__(*args, **kwargs)

    # create_url = "https://stackoverflow.com/questions/tagged/"

    def parse(self, response):
        questions = response.css('.question-summary')
        print("TOTAL QUESTION IN THIS PAGE : ", end="")
        print(len(questions))
        for q in questions:
            stack_question_id = q.css('.question-hyperlink::attr(href)').extract_first().split("/")[2]
            question_title = q.css('.question-hyperlink::text').extract()
            question_content = q.css('.excerpt::text').extract()
            question_url = q.css('.question-hyperlink::attr(href)').extract()
            date_posted = q.css('.relativetime::attr(title)').extract()
            upvote = q.css('.vote-count-post strong::text').extract()
            view = q.css('.views::attr(title)').extract()
            tags = q.css('.post-tag::text').extract()
            answers_count = q.css('.status strong::text').extract()

            stack_user_id = q.css('.user-details a::attr(href)').extract_first().split("/")[2]
            user_name = q.css('.user-details a::text').extract()
            user_reputation_score = q.css('.reputation-score::text').extract()
            user_gold_badges = q.css('.badge1+ .badgecount::text').extract()
            user_silver_badges = q.css('.badge2+ .badgecount::text').extract()
            user_bronze_badges = q.css('.badge3+ .badgecount::text').extract()

            user = {
                'stack_user_id': stack_user_id,
                'name': user_name[0],
                'reputation_score': (user_reputation_score[0]) if len(user_reputation_score) > 0 else 0,
                'gold_badges': (user_gold_badges[0]) if len(user_gold_badges) > 0 else 0,
                'silver_badges': (user_silver_badges[0]) if len(user_silver_badges) > 0 else 0,
                'bronze_badges': (user_bronze_badges[0]) if len(user_bronze_badges) > 0 else 0

            }

            stackoverflow = {
                'stack_question_id': stack_question_id,
                'question_title': question_title[0],
                'question_content': question_content[0],
                'question_url': question_url[0],
                'date_posted': date_posted[0],
                'upvote': (upvote[0]),
                'view': (view[0].split(' ')[0]),
                'tags': tags,
                'answers_count': (answers_count[0]),
                'user': user,
                'answers': []
            }

            if int(answers_count[0]) >= 0:
                question_url = q.css('.question-hyperlink::attr(href)').get()
                yield response.follow(question_url, self.parse_answer, meta={'stackoverflow': stackoverflow})

            next_page = response.css(
                '.s-pagination--item__clear~ .js-pagination-item+ .js-pagination-item::attr(href)').extract_first()
            next_page_text = \
            response.css('.s-pagination--item__clear~ .js-pagination-item+ .js-pagination-item::attr(title)').extract()[
                0].split(' ')[3]
            if next_page is not None and int(next_page_text) < 6:
                next_page_url = "https://stackoverflow.com" + next_page
                yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_answer(self, response):
        item = StackOverflow()
        stackoverflow = response.meta['stackoverflow']

        # QUESTION COMMENT GATHERING START

        questionComments = response.css('#question .js-comment')
        q_comments = []
        for qc in questionComments:
            stack_question_comment_id = qc.css('.js-comment::attr(data-comment-id)').extract_first()
            comment_content = qc.css('.comment-copy::text').extract()
            username = qc.css('.comment-user::text').extract()

            comment = {
                'stack_question_id': stackoverflow['stack_question_id'],
                'stack_question_comment_id': stack_question_comment_id,
                'comment_content': comment_content[0] if len(comment_content) > 0 else ' ',
                'username': username[0] if len(username) > 0 else ''
            }

            q_comments.append(comment)

        # QUESTION COMMENT GATHERING END

        answers = stackoverflow['answers']
        anss = response.css('.answer')

        for a in anss:
            stack_answer_id = a.css('.answer::attr(id)').extract_first().split("-")[1]
            answer_content = a.css('.js-post-body *::text').getall()
            date_posted = a.css('.relativetime::attr(title)').extract()
            upvote = a.css('.ai-center::text').extract()
            accepted = a.css('.d-none::attr(title)').extract()

            stack_user_id = a.css('.user-details a::attr(href)').extract_first().split("/")[2]
            user_name = a.css('.user-details a::text').extract()
            user_reputation_score = a.css('.reputation-score::text').extract()
            user_gold_badges = a.css('.badge1+ .badgecount::text').extract()
            user_silver_badges = a.css('.badge2+ .badgecount::text').extract()
            user_bronze_badges = a.css('.badge3+ .badgecount::text').extract()

            user = {
                'stack_user_id': stack_user_id,
                'name': user_name[0],
                'reputation_score': (user_reputation_score[0]) if len(user_reputation_score) > 0 else 0,
                'gold_badges': (user_gold_badges[0]) if len(user_gold_badges) > 0 else 0,
                'silver_badges': (user_silver_badges[0]) if len(user_silver_badges) > 0 else 0,
                'bronze_badges': (user_bronze_badges[0]) if len(user_bronze_badges) > 0 else 0

            }

            # ANSWER COMMENT GATHERING START

            answerComments = a.css('.js-comment')
            a_comments = []

            for ac in answerComments:
                stack_answer_comment_id = ac.css('.js-comment::attr(data-comment-id)').extract_first()
                comment_content = ac.css('.comment-copy::text').extract()
                username = ac.css('.comment-user::text').extract()

                comment = {
                    'stack_answer_id': stack_answer_id,
                    'stack_answer_comment_id': stack_answer_comment_id,
                    'comment_content': comment_content[0] if len(comment_content) > 0 else ' ',
                    'username': username[0] if len(username) > 0 else ''
                }

                a_comments.append(comment)

            answer = {
                'stack_answer_id': stack_answer_id,
                'answer_content': " ".join(answer_content),
                'date_posted': date_posted[0],
                'upvote': (upvote[0]),
                'accepted': "YES" if len(accepted) == 0 else "NO",
                'user': user,
                'answer_comments': a_comments
            }

            answers.append(answer)

            # ANSWER COMMENT GATHERING END

        stackoverflow['answers'] = answers
        stackoverflow['question_comments'] = q_comments

        item['stack_question_id'] = stackoverflow['stack_question_id']
        item['question_title'] = stackoverflow['question_title']
        item['question_content'] = stackoverflow['question_content']
        item['question_url'] = stackoverflow['question_url']
        item['date_posted'] = stackoverflow['date_posted']
        item['upvote'] = stackoverflow['upvote']
        item['view'] = stackoverflow['view']
        item['tags'] = stackoverflow['tags']
        item['answers_count'] = stackoverflow['answers_count']
        item['answers'] = stackoverflow['answers']
        item['user'] = stackoverflow['user']
        item['question_comments'] = stackoverflow['question_comments']

        yield item

        # yield stackoverflow
