from pprint import pprint
import django
from django.db.models.fields.related import RECURSIVE_RELATIONSHIP_CONSTANT
django.setup()
import scrapy
from scrapy.http import Request, request
from movie.models import Movie, Comment, Genre


class FilimoLinksSpider(scrapy.Spider):
    name = 'filimo_links'
    # allowed_domains = ['https://www.filimo.com/']
    start_urls = ['https://www.filimo.com/movies/']  # the main page
    page_number = 0

    # the page with loading more data
    # start_urls = ['https://www.filimo.com/cms/movie/loadmore/tagid/1000/more_type/infinity/show_serial_parent/1/perpage/200/page/1']

    # get all movie links and save to db with their links

    def parse(self, response):

        print('************* in parse method in spider ************* \n\n\n\n')

        links = response.css(
            'div.item div.ds-movie-item.ui-mb-4x.ui-pt-2x a::attr(href)').getall()

        for link in links:
            if not Movie.objects.filter(original_url = link).exists():
                yield Request(link, callback=self.parse_movie_page)
            else:
                print('duplicate url pass here')


        # # for page_number in range(1, 50):
        print(f'page in number ***********{self.page_number}********* \n')
        self.page_number += 1
        next_page = f'https://www.filimo.com/cms/movie/loadmore/tagid/1000/more_type/infinity/show_serial_parent/1/perpage/200/page/{self.page_number}'
        if self.page_number > 50:  # with 200 movies per page and the movie number of 10,000
            return None
        yield Request(next_page, callback=self.parse)

    def parse_movie_page(self, response):
        print('************* in parse movie page ********************\n\n\n\n ')
    
        raw_genre= response.css(' li.ui-ml-2x a.ui-btn.ui-btn-force-dark.ui-btn-small.ui-br-24.ui-pr-2x.ui-pl-2x.ui-pt-x.ui-pb-x.ui-bg-gray-20.details_poster-description-meta-link span::text').getall()
        genre_obj =Genre.objects.filter(fname__in =raw_genre )

        movie_obj = Movie.objects.create(
            code=response.url[25:30],
            original_url=response.url,
            ename=response.css(
                'p.en-title.ui-fw-normal.ui-fs-medium.force-text-en.d-inline-bock::text').get(),
            fname=response.css(
                'h1.details_poster-description-title div.fa-title.ui-fw-semibold::text').get(),
            summary=response.css(
                'div.gallery_left-side.float-left.md-ui-pr-0 div.gallery_each-movie.ui-mb-8x p.toTruncate.ps-relative::text').get(),
            imdb_rating=response.css(
                'div.ds-badge.ds-badge--icon.ds-badge--brand.imdb span.ds-badge_label span.en.ui-fc-black.ui-fw-bold::text').get(),
            filimo_rating=response.xpath('//*[@id="percentNumber"]/text()').get(),
            filimo_total_votes=response.xpath('//*[@id="rateCnt"]/text()').get(),
            image_url = response.xpath('/html/body/div[1]/main/div/div[1]/div/div[3]/div[1]/div[1]/div/div/div[1]/img/@data-src').get()

            
            # TODO get the genres later
        )
        movie_obj.genres.add(*genre_obj)

        comments = response.css('li.comment-item.clearfix')
        for comment in comments: #TODO spoiler commetns
            text=comment.css('div.comment-left-side div.comment-body p.comment-content::text').get()
                
            c = Comment.objects.create(
                movie=movie_obj,
                text = text,
                date=comment.css(
                    'div.comment-left-side div.comment-info.clearfix span.comment-date::text').get(),
                vote_up=comment.css(
                    'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-up.set-query.open-modal.is-ajax-button i.like-count::text').get(),
                vote_down=comment.css(
                    'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-down.set-query.open-modal.is-ajax-button i.like-count::text').get(),
            )
            c.save()

        # TODO check if more comments is there
        if response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::text').get():
            next_comment_page = response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::attr(data-href)').get()
            return Request(url=f'https://www.filimo.com{next_comment_page}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))
        return None

    # to get the comments that loads after pressing more comments in each movie page (if exitst)
    def parse_movie_comment(self, response, movie_obj):
        print('*********************** parse_movie_comment ******************** \n ')

        comments = response.css('li.comment-item.clearfix')
        for comment in comments:
            c = Comment.objects.create(
                movie=movie_obj,
                text=comment.css(
                    'div.comment-left-side div.comment-body p.comment-content::text').get(),
                date=comment.css(
                    'div.comment-left-side div.comment-info.clearfix span.comment-date::text').get(),
                vote_up=comment.css(
                    'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-up.set-query.open-modal.is-ajax-button i.like-count::text').get(),
                vote_down=comment.css(
                    'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-down.set-query.open-modal.is-ajax-button i.like-count::text').get(),
            )
            c.save()
        if response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::text').get():
            next_comment_page = response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::attr(data-href)').get()
            return Request(url=f'https://www.filimo.com{next_comment_page}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))
        else:
            return None

        # return Request(url='url', callback=self.parse_movie_comment) if response.css('').get() else None


