from icecream import ic
from scrapy import Request
import scrapy
import django
django.setup()
from movie.models import Movie, Comment, Genre
# url of movie and serie are the same just 1000 is for movie and 1001 is for serie
MOVIE_URL = 'https://www.filimo.com/cms/movie/loadmore/tagid/1000/more_type/infinity/show_serial_parent/1/perpage/200/page/'
SERIE_URL = MOVIE_URL.replace('1000', '1001')


class CSSPathSource(object):
    """css path using in body of spider is here to keep the code clean"""

    movie_links_path = 'div.item div.ds-movie-item.ui-mb-4x.ui-pt-2x a::attr(href)'
    movie_genres_path = 'li.ui-ml-2x a.ui-btn.ui-btn-force-dark.ui-btn-small.ui-br-24.ui-pr-2x.ui-pl-2x.ui-pt-x.ui-pb-x.ui-bg-gray-20.details_poster-description-meta-link span::text'
    movie_ename_path = 'p.en-title.ui-fw-normal.ui-fs-medium.force-text-en.d-inline-bock::text'
    movie_fname_path = 'h1.details_poster-description-title div.fa-title.ui-fw-semibold::text'
    movie_summary_path = 'div.gallery_left-side.float-left.md-ui-pr-0 div.gallery_each-movie.ui-mb-8x p.toTruncate.ps-relative::text'
    movie_imdb_rating = 'div.ds-badge.ds-badge--icon.ds-badge--brand.imdb span.ds-badge_label span.en.ui-fc-black.ui-fw-bold::text'
    movie_filimo_rating_path = '//*[@id="percentNumber"]/text()'
    movie_filimo_total_votes = '//*[@id="rateCnt"]/text()'
    movie_image_url = '/html/body/div[1]/main/div/div[1]/div/div[3]/div[1]/div[1]/div/div/div[1]/img/@data-src'
    comment_section = 'li.comment-item.clearfix'
    comment_text = 'div.comment-left-side div.comment-body p.comment-content::text'
    comment_date = 'div.comment-left-side div.comment-info.clearfix span.comment-date::text'
    comment_vote_up = 'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-up.set-query.open-modal.is-ajax-button i.like-count::text'
    coomet_vote_down = 'div.comment-left-side div.comment-info.clearfix div.rate.clearfix span.like button.request-link.like-item.thumbs-down.set-query.open-modal.is-ajax-button i.like-count::text'
    comment_other_episode_section = 'button#parentComments.request-link.comments-loadmore.ui-pt-2x.ui-pb-2x.ui-pr-3x.ui-pl-3x.pointer.ui-fc-white.is-ajax-button::attr(data-href)'
    next_page_comment = 'div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::attr(data-href)'
    load_more_comment_button = 'div.center.loadmore-link button#comments-loadmore.request-link.comments-loadmore.is-ajax-button::text'


csspath = CSSPathSource()


class FilimoLinksSpider(scrapy.Spider):
    type = 1  # type 0 is for movie and 1 is for series, it will be used in downloading pages
    name = 'filimo_links'
    start_urls = [MOVIE_URL + str(page) for page in range(1, 55)] + [SERIE_URL+str(page) for page in range(1,20)]

    def parse(self, response):
        """find all movie page link and pass it to detail parsers"""

        print('************* in parse method in spider ************* \n\n')
        links = response.css(csspath.movie_links_path).getall()
        for link in links:  # for each links found in movie/series list, send a request with that link to parse in movie page
            if not Movie.objects.filter(original_url=link).exists():#TODO: just for testing remove the second if
                yield Request(link, callback=self.parse_movie_page)
            else:  # TODO: pass it all in case of facing the first duplicate movie
                # ic('duplicate url pass here')
                pass
        return None

    def parse_movie_page(self, response):
        print('************* in parse movie page *************\n\n')

        # saving movie data
        movie_obj = Movie.objects.create(
            code=response.url[25:30],
            original_url=response.url,
            ename=response.css(csspath.movie_ename_path).get(),
            fname=response.css(csspath.movie_fname_path).get(),
            summary=response.css(csspath.movie_summary_path).get().replace('\n', ''),
            imdb_rating=response.css(csspath.movie_imdb_rating).get(),
            filimo_rating=response.xpath(csspath.movie_filimo_rating_path).get(),
            filimo_total_votes=response.xpath(csspath.movie_filimo_total_votes).get(),
            image_url=response.xpath(csspath.movie_image_url).get(),
            )
        #saving genres for this movie
        raw_genre = response.css(csspath.movie_genres_path).getall()
        ic()
        genre_objs = Genre.objects.filter(fname__in=raw_genre)
        movie_obj.genres.add(*genre_objs)

        # get comments in first loading of movie page
        self.save_comments(response, movie_obj)

        if response.css(csspath.load_more_comment_button).get():
            next_page_path = response.css(csspath.next_page_comment).get()
            next_page_path = next_page_path.replace('/20/','/1000/')
            next_url = f'https://www.filimo.com{next_page_path}'
            return Request(url=next_url , callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj), dont_filter=True)
        return None

    def parse_movie_comment(self, response, movie_obj):
        """get all the comments for a movie page"""
        print('*********************** parse_movie_comment ******************** \n ')

        self.save_comments(response, movie_obj)

        if len(other_episode_comments := response.css(csspath.comment_other_episode_section).getall()) > 0:
            print('\n\n\n\nin if for going for the serie comments sssssssssss \n\n\n\n\n')
            for link in other_episode_comments:
                yield Request(url=f'{link}', callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj))

        if response.css(csspath.load_more_comment_button).get():
            next_page_path = response.css(csspath.next_page_comment).get()
            # next_page_path  = next_page_path.replace('/20/', '/1000/')
            ic(next_page_path)
            next_url = f'https://www.filimo.com{next_page_path}'
            return Request(url=next_url, callback=self.parse_movie_comment, cb_kwargs=dict(movie_obj=movie_obj), dont_filter=True)
        else:
            return None

    def save_comments(self, response, movie_obj):
        ic('this is saving comment method for a reponse')
        """saving all of the comment comming from a response"""
        comments = response.css(csspath.comment_section)
        for comment in comments:
            text = comment.css(csspath.comment_text).get()
            if text not in ['\n', '', ' ']:
                c = Comment.objects.create(
                    movie=movie_obj,
                    text=text.replace('\n', ''),
                    date=comment.css(csspath.comment_date).get(),
                    vote_up=comment.css(csspath.comment_vote_up).get(),
                    vote_down=comment.css(csspath.coomet_vote_down).get(),
                )
                c.save()
        return None
