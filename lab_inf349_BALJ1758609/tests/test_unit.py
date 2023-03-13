
import pytest

from inf349.models import Product, Order

class TestProduct(object):
    def test_init(self): #creation d'un produit et verifier si tout est dedans 
        productTest = Product(name="choucoutre", 
                              description="bonne appetit!",
                              image="attention.jpg",
                              weight=1300,
                              price=1.200,
                              in_stock=True)
        #partie verification 
        assert productTest.name == "choucoutre"
        assert productTest.description == "bonne appetit!"
        assert productTest.image == "attention.jpg"
        assert productTest.weight == 1300
        assert productTest.price == 1.200
        assert productTest.in_stock == True 

class TestOrder(object):
    def test_init(self): #creation d'un order et verifier que tout est dedans 
        product1 = Product(name="choucoutre", 
                           description="bonne appetit!",
                           image="choucoutre.jpg",
                           weight=300,
                           price=1.200,
                           in_stock=True)      
        orderTest = Order(total_price=2.70,
                          email="test@example.com",
                          credit_card={ "name" : "John Doe",
                                          "number" : "4242 4242 4242 4242",
                                           "expiration_year" : 2024,
                                            "cvv" : "123", "expiration_month" : 9 },
                          shipping_information= { "country" : "Canada",
                                                    "address" : "201, rue Président-Kennedy",
                                                      "postal_code" : "G7X 3Y7",
                                                        "city" : "Chicoutimi",
                                                          "province" : "QC" }, 
                          paid=False,
                          transaction={},
                          product={"product": {"id": product1.id, "quantity": 2}},
                          shipping_price=0.50)
        #partie verification 
        assert orderTest.total_price == 2.70
        assert orderTest.email == "test@example.com"
        assert orderTest.credit_card == { "name" : "John Doe",
                                          "number" : "4242 4242 4242 4242",
                                           "expiration_year" : 2024,
                                            "cvv" : "123", "expiration_month" : 9 }
        assert orderTest.shipping_information == { "country" : "Canada",
                                                    "address" : "201, rue Président-Kennedy",
                                                      "postal_code" : "G7X 3Y7",
                                                        "city" : "Chicoutimi",
                                                          "province" : "QC" }
        assert orderTest.paid == False
        assert orderTest.transaction == {}
        assert orderTest.product == {"product": {"id": product1.id, "quantity": 2}}
        assert orderTest.shipping_price == 0.50
    def test_to_totalPrice(self):#test de la methode total_price vu qu'elle ne dépend de personne 
        product1 = Product(name="choucoutre", #on attend un total_price definit à l'avance selon le weight et le price 
                           description="bonne appetit!",
                           image="choucoutre.jpg",
                           weight=300,
                           price=12,
                           in_stock=True)
        orderTest = Order()
        orderTest.to_totalPrice(product1.price, 3)
        assert orderTest.total_price == 36    
    def test_to_shippingPrice(self): 
        #faute de temps et de compréhension des tests fonctionnels j'ai mis ce test ici
        #mais il devrait etre dans le focntionnel car il dépend de total_price 
        product1 = Product(name="choucoutre", 
                           description="bonne appetit!",
                           image="choucoutre.jpg",
                           weight=300,
                           price=12,
                           in_stock=True)
        orderTest = Order()
        orderTest.to_totalPrice(product1.price, 3)
        orderTest.to_shippingPrice(product1.weight, 3)
        assert orderTest.shipping_price == 46