import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import time
from flask import Flask, render_template, request

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)


@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review", methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            # searchString = request.form['content'].replace(" ", "")
            product_link = request.form.get('product_link')
            # searchString = request.form.get('content').replace(" ", "")
            product_name = request.form.get('product_name')
            # flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            # urlclient = urlopen(flipkart_url)
            # flipkart_page = urlclient.read()
            # flipkart_soup = bs(flipkart_page, "html.parser")
            # flipkart_items_div = flipkart_soup.find_all(class_="cPHDOP col-12-12")

            if not product_link:
                logging.info("No products found on Flipkart for the review.")
                return "No review found."

            final_Reviews_container = []     
            logging.info(f'Product Link: {product_link}')   
            time.sleep(1)  # Add delay to prevent HTTP 429 error
            try:
                product_req = urlopen(product_link)
                product_req = product_req.read()
                product_soup = bs(product_req, "html.parser")
                reviews_container = product_soup.find_all(class_="RcXBOT")
                    
                for each_review_container in reviews_container:
                    try:
                        name_tag = each_review_container.div.div.find_all(class_="row gHqwa8")[0]
                        rating_tag = each_review_container.div.div.find_all(class_="row")[0].div
                        comment_head_tag = each_review_container.div.div.find_all(class_="row")[0].p    
                        actual_comment_tag = each_review_container.div.div.find_all(class_="row")[1].div.div.div

                        if name_tag and rating_tag and comment_head_tag and actual_comment_tag:
                            name = name_tag.p.string
                            rating = rating_tag.text
                            comment_head = comment_head_tag.text
                            actual_comment = actual_comment_tag.text

                            review_dict = {
                                    "Product": product_name,
                                    "Name": name,
                                    "Rating": rating,
                                    "CommentHead": comment_head,
                                    "Comment": actual_comment
                                }
                            final_Reviews_container.append(review_dict)
                            
                    except Exception as e:
                        logging.error(f"Error processing individual review: {e}")
                        continue
            except Exception as e:
                logging.error(f"Error fetching product page: {e}")

            if not final_Reviews_container:
                return "No reviews found , Please try again."

            logging.info(f"Final reviews: {final_Reviews_container}")
            return render_template('result.html', reviews=final_Reviews_container)
        except Exception as e:
            logging.error(f"Error in main process: {e}")
            return f'Something went wrong: {e}'
    else:
        return render_template('index.html')
    


@app.route("/result", methods=['POST', 'GET'])
def landing():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            urlclient = urlopen(flipkart_url)
            flipkart_page = urlclient.read()
            flipkart_soup = bs(flipkart_page, "html.parser")
            flipkart_items_div=flipkart_soup.find_all(class_="cPHDOP col-12-12")
            del flipkart_items_div[0:3]
            print(len(flipkart_items_div))
            if not flipkart_items_div:
                logging.info("No products found on Flipkart for the search string.")
                return "No products found."

            final_Reviews_container = []
            for flipkart_item in flipkart_items_div:
                product_link_tag = flipkart_item.find("a")
                if product_link_tag is None:
                    continue

                product_link = "https://www.flipkart.com" + product_link_tag["href"]
                logging.info(f'Product Link: {product_link}')
                
                time.sleep(1)  # Add delay to prevent HTTP 429 error
                try:
                    product_req = urlopen(product_link)
                    product_req = product_req.read()
                    # product_soup = bs(product_req, "html.parser")
                    product_soups=bs(product_req, "html.parser")
                    
                    for each_product_soup in product_soups:
                        try:
                            name_container=each_product_soup.find_all(class_="VU-ZEz")
                            # product overall rating
                            over_all_rating_container=each_product_soup.find_all(class_="Y1HWO0")
                            # product price
                            price_container=each_product_soup.find_all(class_="Nx9bqj CxhGGd")  
                            offer_container=each_product_soup.find_all(class_="+-2B3d row")
                            img_container=each_product_soup.find_all(class_="_4WELSP _6lpKCl")
                            dis_product_container=each_product_soup.find_all(class_="yRaY8j A6+E6v")
                            dis_offer_price_container=each_product_soup.find_all(class_="UkUFwK WW8yVX")
                            if name_container and over_all_rating_container and price_container and img_container:
                                product_name=name_container[0].text
                                over_all_rating=over_all_rating_container[0].div.text
                                product_price=price_container[0].text
                                dis_product_price=dis_product_container[0].text
                                dis_offer_price=dis_offer_price_container[0].span.text
                                # logging.info(dis_offer_price,dis_product_price)
                                product_offers=[]
                                for product_offer in offer_container:
                                    offer_detail=product_offer.li.find_all("span")
                                    for i in offer_detail:
                                        word_count = len((i.text).split())
                                        if word_count <= 3:
                                             continue    
                                        bank_offer=i.text
                                        product_offers.append(bank_offer)
                                product_img=img_container[0].img.get("src")
                                print(product_offers)
                                product_dict = {
                                    "product_name": product_name,
                                    "over_all_rating":over_all_rating,
                                    "product_price": product_price,
                                    "dis_product_price":dis_product_price,
                                    "dis_offer_price":dis_offer_price,
                                    "product_offers": product_offers,
                                    "product_img": product_img,
                                    "product_link": product_link
                                }
                                final_Reviews_container.append(product_dict)
                                
                        except Exception as e:
                            logging.error(f"Error processing individual review: {e}")
                            continue
                except Exception as e:
                    logging.error(f"Error fetching product page: {e}")
                    continue

            if not final_Reviews_container:
                return "No reviews found."

            logging.info(f"Final reviews: {final_Reviews_container}")
            return render_template('landing.html', reviews=final_Reviews_container)
        except Exception as e:
            logging.error(f"Error in main process: {e}")
            return f'Something went wrong: {e}'
    else:
        return render_template('index.html')
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
