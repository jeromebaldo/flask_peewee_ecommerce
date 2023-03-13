from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from peewee import SqliteDatabase
import click
import requests
import json

from inf349.models import Product, Order

class API_Ext_Services(object):
    @classmethod
    def update_products(cls):
        # Récupération des produits depuis l'API externe
        response = requests.get('http://dimprojetu.uqac.ca/~jgnault/shops/products/')
        data = response.json()

        # Suppression des produits existants dans la base de données
        Product.delete().execute()

        # Ajout des nouveaux produits à la base de données
        for product_data in data['products']:
            product = Product.create(
                id=product_data['id'],
                name=product_data['name'],
                description=product_data['description'],
                image=product_data['image'],
                weight=product_data['weight'],
                price=product_data['price'],
                in_stock=product_data['in_stock']      
            )
    @classmethod
    def to_verifCard(cls,data):
        #verifier que les expiration year et month sont des integer car l'APi externe ne verifie pas ces champs  
        if not isinstance(data['credit_card']['expiration_year'], int) or not isinstance(data['credit_card']['expiration_month'], int) :
            return {'error':  { "order": { "code": "error-field", "name": "année d'expiration ou/et mois expiration invalide " } }, 'code' : 422}
        #verifier qu'il y a tous les champs requis sont présent dans credit_card 
        if 'name' not in data['credit_card'] or 'number' not in data['credit_card'] or 'expiration_year' not in data['credit_card'] or 'cvv' not in data['credit_card'] or  'expiration_month' not in data['credit_card']:
            return {'error':  { "order": { "code": "error-field", "name": "il manque des champs ou/et certains sont nuls" } }, 'code' : 422}
        else:
            url = 'http://dimprojetu.uqac.ca/~jgnault/shops/pay/'
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                transaction_data = response.json()
                return {'transaction' : transaction_data, 'code' : 200}
            else:
                error_data = response.json().get('errors')
                return {'error': error_data, 'code' : response.status_code}
class API_Inter_Product_Services(object):
    #recupère tous les produits présents dans la base de données 
    @classmethod
    def list_Total_Product(cls):
        products = Product.select()
        product_list = []
        for product in products:
            product_ligne = {'id': product.id,
                'name': product.name,
                'description': product.description,
                'image' : product.image,
                'weight' : product.weight,
                'price': product.price,
                'in_stock': product.in_stock}
            product_list.append(product_ligne)
        return product_list
    #methode pour verifier si le prouit existe dans la base de données 
    # s'il n'existe pas alors retourne un code 404 avec json 
    @classmethod
    def exist_product(cls,request):
        try:
            product_id = request.json['product']['id']
            quantity = request.json['product']['quantity']
        except (KeyError, TypeError):
            return {
                'errors': {
                    'product': {
                        'code': 'missing-fields',
                        'name': "La création d'une commande nécessite un produit"
                    }
                }
            ,'code': 422}
        return {'code': 200}
    #methode pour verifier si le json client n'a pas plusieurs produits rentrés dedans
    #si il y a plusieurs produits alors retourne code d'erreur avec json 
    @classmethod
    def solo_product(cls,request):
        if len(request.json.get('product', {}).keys()) != 2:
            return {
                'errors': {
                    'product': {
                        'code': 'invalid-product',
                        'name': "Une commande ne peut recevoir qu'un seul produit"
                    }
                }
            , 'code': 422}
        return {'code': 200}
    #verifie si la quantite demandee est egale et superieure à 1
    #si ce n'est pas le cas renvi du code 422 et d'un json d'informations 
    @classmethod
    def qtite_product(cls, quantity):
        if quantity < 1:
            return {
                'errors': {
                    'product': {
                        'code': 'missing-fields',
                        'name': "La quantité doit être supérieure ou égale à 1"
                    }
                }
            , 'code': 422}
        return {'code': 200}
    #methode pour consulter si le produit est en stock
    #verifie la variable in_stock == true si négatif alors renvoi code erreur avec json 
    #permet aussi de prendre en compte si le produit existe tout simplement dans la bd 
    @classmethod
    def stock_product(cls, product_id):
        try:
            product = Product.get(Product.id == product_id, Product.in_stock == True)
        except Product.DoesNotExist:
            return {
                'errors': {
                    'product': {
                        'code': 'out-of-inventory',
                        'name': "Le produit demandé n'est pas en inventaire"
                    }
                }
            , 'code': 422}
        
        return {'code': 200}
class API_Inter_Order_Services(object):    
    #methode pour créer un ordre et l'ajouter dans la bd
    #calcul le total_price et le shipping price 
    @classmethod
    def crea_order(cls, product_id, quantity):
        product_select = Product.get(Product.id == product_id)
        #vu que pas préciser et faute de temps je n'ai pas mis de foreign key pour l'id du product
        order = Order.create(product={'id':product_select.id, 'quantity':quantity})
        Order.to_totalPrice(order, product_select.price, quantity)#appel methode d'order 
        Order.to_shippingPrice(order, product_select.weight,quantity)#appel methode d'order 
        order.save()
        return { 'id': order.id}
    #methode pour verifier si l'order existe dans la base de données 
    #si non alors retourne code d'erreur 404 avec json adapté
    @classmethod
    def exist_order(cls,order_id):
        try:
            orderGet = Order.get(Order.id == order_id)
        except Order.DoesNotExist:
            error = {
                'order': {
                    'code': 'not-found',
                    'name': "La commande spécifiée n'existe pas"
                }
            }
            return {  'error' : error ,'code': 404}
        return {'code' : 200}
    #methode pour retourner l'order demandé avec tous les champs remplis ou non
    @classmethod
    def return_order(cls,order_id):
        orderGet = Order.get(Order.id == order_id)
        return {'order' : {
            'id': orderGet.id,
            'total_price': orderGet.total_price,
            'email' : orderGet.email,
            'credit_card': orderGet.credit_card,
            'shipping_information': orderGet.shipping_information,
            'paid': orderGet.paid,
            'transaction' : orderGet.transaction,
            'product': {
                'id': orderGet.product['id'],
                'quantity': orderGet.product['quantity'],
            },
            'shipping_price': orderGet.shipping_price 
        }, 'code' : 200}
    @classmethod
    def put_order_infoClient(cls,order_id,data):
    
        #verification e l'existence de l'order avec son id si négatif alors retourne 404 
        response = API_Inter_Order_Services.exist_order(order_id)
        if response['code'] == 404:
            return {'error' : response['error'], 'code' : response['code']}
        else:
            orderModif = Order.get(Order.id == order_id) #recuperation de l'order     
    
        try:#ajout de l'email et des informations de shipping
            emailRecu = data['order']['email']
            shippingInfoRecu = data['order']['shipping_information']
        except (KeyError, TypeError):
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il faut les informations clients pour compléter la commande"
                    }
                }   
            return {  'error' : error ,'code': 422}
    
        # Vérifier si tous les champs requis sont présents
        verif_champShipping = data['order']['shipping_information']
        if 'country' not in verif_champShipping or 'address' not in verif_champShipping or 'postal_code' not in verif_champShipping or 'city' not in verif_champShipping or 'province' not in verif_champShipping or 'email' not in data['order']: 
            error = {
                    'order': {
                        'code': 'missing-fields',
                        'name': "Il manque un ou plusieurs champs qui sont obligatoires"
                    }
                }
            return {  'error' : error ,'code': 422}
        
        # Vérifier qu'aucun champ autre que email et shipping_information n'est modifié
        if 'transaction' in data['order'] or 'product' in data['order'] or 'id' in data['order'] or 'shipping_price' in data['order'] or 'total_price' in data['order'] or 'paid' in data['order']:
            error = {
                    'order': {
                        'code': 'invalid-fields',
                        'name': "Certains champs ne peuvent pas être modifiés par cette requête"
                    }
                }
            return {'error' : error ,'code': 422}
        #enregistrement de l'email et des informations sur le shippping puis  sauvegarde des moifcations 
        orderModif.email = emailRecu
        orderModif.shipping_information = shippingInfoRecu
        orderModif.save()
        #return de l'order complété à afficher pour l'init 
        response = API_Inter_Order_Services.return_order(orderModif.id)
        return {'order' : response['order'] ,'code': response['code']}
    @classmethod
    def put_order_paiement(cls,order_id,data):
        
        #verifier que l'order existe dans la base de données 
        response = API_Inter_Order_Services.exist_order(order_id)
        if response['code'] == 404:
            return {'error' : response['error'], 'code' : response['code']}
        else:
            order_paiement = Order.get(Order.id == order_id)
        #verifier et obliger le client à remplir l'email et le shippinginformation avant de payer 
        if order_paiement.email is None or order_paiement.shipping_information is None:
            return { 'error' : {'errors' : { "order": { "code": "missing-field", "name": "l'email et/ou les informations d'expéditions n'ont été rentrées " } } }, 'code': 422}
        # si paid  == true alors la commande est déjà payé et retourne 422 avec json d'informations 
        if order_paiement.paid == True:
            return { 'error' : {'errors' : { "order": { "code": "already-paid", "name": "La commande a déjà été payée." } } }, 'code': 422}
        else:
            #appel à la methode des API externes pour verifier si la carte est bonne
            # si ok alors API externe renvoie 200 avec json sur la transaction qui a reussi 
            # si KO alors APi externe renvoi code erreur avec json 
            json_response = API_Ext_Services.to_verifCard(data)
            #mise à jour des informations de paiements et de la transaction 
            if json_response['code'] == 200:
                order_paiement.credit_card = json_response['transaction']['credit_card']
                order_paiement.transaction = json_response['transaction']['transaction']
                order_paiement.paid = True
                order_paiement.save()
                response = API_Inter_Order_Services.return_order(order_paiement.id)
                return {'order' : response['order'] ,'code': response['code']} 
            else:
                #mise à jour des informations sur la credit_card et pour la transaction 
                order_paiement.credit_card = data['credit_card']
                if 'amount_charged' in data:
                    order_paiement.transaction = {'errors' : json_response['error'], 'amount_charged': data['amount_charged'] }
                else:
                    order_paiement.transaction = {'errors' : json_response['error']}   
                order_paiement.save()
                return {'error': json_response['error'], 'code' : json_response['code']}