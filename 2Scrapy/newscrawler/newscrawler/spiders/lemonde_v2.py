import scrapy

class LemondeSpider(scrapy.Spider):
    name = "lemondev2"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response):
        title = response.css("title::text").get(default="").strip()

        # Liens des catégories (left sidebar)
        categories = response.css("ul.nav.nav-list li a")
        for cat in categories:
            name = cat.css("::text").get().strip()
            url = response.urljoin(cat.attrib["href"])

            # Affichage propre (avec sauts de ligne)
            self.log(f"\n---- Nouvelle catégorie trouvée ----\n"
                     f"Nom : {name}\n"
                     f"URL : {url}\n")

            # On suit chaque lien
            yield scrapy.Request(url, callback=self.parse_category, meta={"category": name})

    def parse_category(self, response):
        category = response.meta["category"]
        page_title = response.css("title::text").get(default="").strip()

        self.log(f"\n===== PAGE CATÉGORIE =====\n"
                 f"Catégorie : {category}\n"
                 f"Titre de la page : {page_title}\n")
        yield {
            "category": category,
            "page_title": page_title,
        }