import scrapy
from scrapy import Request


class Lemondev2Spider(scrapy.Spider):
    name = "lemondev3"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def clean_spaces(self, string):
        if string:
            return " ".join(string.split())
        return string

    def parse(self, response):
        """
        1. Récupère les liens des catégories
        2. Crée une Request vers chaque catégorie
        (exactement comme dans le tuto Le Monde)
        """

        # Toutes les catégories sauf le premier élément "Books"
        categories = response.css("ul.nav.nav-list li ul li a")

        for cat in categories:
            name = self.clean_spaces(cat.css("::text").get())
            url = response.urljoin(cat.attrib["href"])

            # Debug propre avec sauts de ligne (comme le tuto)
            self.log(
                f"\n---- Nouvelle catégorie ----\n"
                f"Nom : {name}\n"
                f"URL : {url}\n"
            )

            # ON ENVOIE VERS parse_category
            yield Request(
                url,
                callback=self.parse_category,
                meta={"category": name},
            )

    def parse_category(self, response):
        """
        1. Récupère tous les articles (livres) de la catégorie
        2. Yield un dictionnaire simple pour chaque livre
        (comme lemonde2)
        """

        category = response.meta["category"]

        # Sélecteur équivalent à .river > .teaser, mais version BooksToScrape
        for article in response.css("article.product_pod"):

            # Titre du livre
            title = article.css("h3 a::attr(title)").get()

            # Image (relative → absolue)
            image_rel = article.css("img::attr(src)").get()
            image = response.urljoin(image_rel)

            # Prix
            price = article.css(".price_color::text").get()

            # Description = pas disponible dans la liste → on simule comme le tuto
            description = article.css("p::text").get()  # souvent None → ok

            yield {
                "category": category,
                "title": self.clean_spaces(title),
                "image": image,
                "price": price,
                "description": self.clean_spaces(description),
            }

        # Gestion pagination (équivalent à descendre dans les sous-pages)
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category,
                meta={"category": category},
            )