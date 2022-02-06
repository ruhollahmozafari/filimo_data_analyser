from json.tool import main
import django
django.setup()
import scrapy
from scrapy.http import Request
from movie.models import Movie, Comment, Genre
from icecream import ic
MOVIE_URL = 'https://www.filimo.com/cms/movie/loadmore/tagid/1000/more_type/infinity/show_serial_parent/1/perpage/200/page/'
SERIE_URL = MOVIE_URL.replace('1000', '1001') # url of movie and serie are the same just 1000 is for movie and 1001 is for serie

class FilimoLinksSpider(scrapy.Spider):
    type = 1 # type 0 is for movie and 1 is for series, it will be used in downloading pages
    name = 'filimo_links'
    # allowed_domains = ['https://www.filimo.com/']
    start_urls = [MOVIE_URL+ str(page) for page in range(1,55)] + [SERIE_URL+str(page) for page in range(1,10) ] 

    def parse(self, response):  
        """find all movie page link and pass it to detail parsers"""

        print('************* in parse method in spider ************* \n\n\n\n')

        links = response.css(
            'div.item div.ds-movie-item.ui-mb-4x.ui-pt-2x a::attr(href)').getall()

        for link in links:
            if not Movie.objects.filter(original_url = link).exists():
                yield Request(link, callback=self.parse_movie_page)
            else:
                ic('duplicate url pass here')
        

        return None


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

        )
        
        movie_obj.genres.add(*genre_obj)
        # get comments in first loading of movie page
        comments = response.css('li.comment-item.clearfix')
        for comment in comments:
            text=comment.css('div.comment-left-side div.comment-body p.comment-content::text').get()
            if text not in ['\n', '', ' ']:                
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

        if response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::text').get():
            next_comment_page = response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::attr(data-href)').get()
            return Request(url=f'https://www.filimo.com{next_comment_page}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))
        return None

    # to get the comments that loads after pressing more comments in each movie page (if exitst)
    def parse_movie_comment(self, response, movie_obj):
        """get all the comments for a movie page"""
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
        
        if len(other_episode_comments := response.css('button#parentComments.request-link.comments-loadmore.ui-pt-2x.ui-pb-2x.ui-pr-3x.ui-pl-3x.pointer.ui-fc-white.is-ajax-button::attr(data-href)').getall())> 0:
            for link in other_episode_comments:
                yield Request(url=f'{link}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))

        if  (next_comment_page := response.css('div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::attr(data-href)').get()):
            return Request(url=f'https://www.filimo.com{next_comment_page}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))
        else:
            return None



