from flask import Flask, jsonify, redirect, url_for, request
from flask.cli import with_appcontext
from inf349.models import init_app, Product, Order
from inf349.services import API_Ext_Services
from inf349.services import API_Inter_Product_Services
from inf349.services import API_Inter_Order_Services


def create_app(initial_config=None):
    app = Flask("inf349")
    init_app(app)
    #methode permettant de remettre à jour la table produits à chaque lancement de l'applciation 
    @app.before_first_request
    def update_on_start():
        if Product.table_exists(): # pour eviter la collision entre init-db et la mise à jour 
            API_Ext_Services.update_products()         
    update_on_start()# appel à la méthode de mise à jour pour la table product 

    @app.route('/', methods=['GET'])
    def get_products():
        product_list = []
        product_list = API_Inter_Product_Services.list_Total_Product()
        return jsonify({"products": product_list}), 200

    @app.route('/order', methods=['POST'])
    def create_order():#creation d'un order 
        #1er ETAPE verifier le produit existe 
        response = API_Inter_Product_Services.exist_product(request)
        if response['code'] != 200:
            return jsonify(response['errors']), response['code']    
        #2e ETAPE verifier qu'il n'y a qu'un seul produit de demandé
        response = API_Inter_Product_Services.solo_product(request)
        if response['code'] != 200:
            return jsonify(response['errors']), response['code'] 
        #RECUPERATION EFFECTIVE DES DATAS
        product_id = request.json['product']['id']
        quantity = request.json['product']['quantity']
        #3e ETAPE verifier que la quantite est supérieur ou égale à 1
        response = API_Inter_Product_Services.qtite_product(quantity)
        if response['code'] != 200:
            return jsonify(response['errors']), response['code']
        #4e ETAPE verifier que le produit est en stock
        response = API_Inter_Product_Services.stock_product(product_id)
        if response['code'] != 200:
            return jsonify(response['errors']), response['code']
        #5e ETAPE - CREATION DE L'ORDER
        response = API_Inter_Order_Services.crea_order(product_id, quantity)
        #6e ETAPE - AFFICHAGE DU LIEN DU GET POUR LA COMMANDE CIBLE
        lien_order = url_for('get_order', order_id = response['id'] , _external=True)
        return jsonify({'lien_order': lien_order})

    @app.route('/order/<int:order_id>', methods=['GET'])
    def get_order(order_id):

        #1er ETAPE verifier que l'order est bien enregistré dans la base 
        response = API_Inter_Order_Services.exist_order(order_id) 
        if response['code'] != 200:
            return jsonify(response['error']), response['code']
        # 2e ETAPE - retourner le json de l'order cible 
        response = API_Inter_Order_Services.return_order(order_id)
        return jsonify(response['order']), response['code']

    @app.route('/order/<int:order_id>', methods=['PUT'])
    def verif_put(order_id):
        data = request.get_json()
        #AIGUILLAGE SELON L'ENVOI DU JSON CLIENT si credit_card alors put_order_paiement sinon si order alors put_order
        #RECPETIONNE LES REPONSES POUR LES METHODES ET LES ENVOIE AU CLIENT 
        if 'order' in data:
            respons_emailShipp = API_Inter_Order_Services.put_order_infoClient(order_id, data)
            if respons_emailShipp['code'] == 200:
                return jsonify(respons_emailShipp['order']), respons_emailShipp['code']
            else:
                return jsonify(respons_emailShipp['error']), respons_emailShipp['code'] 
        if 'credit_card'in data: 
            respons_emailShip = API_Inter_Order_Services.put_order_paiement(order_id, data)
            if respons_emailShip['code'] == 200 :
                return jsonify(respons_emailShip['order']), respons_emailShip['code']
            else:
                return jsonify(respons_emailShip['error']), respons_emailShip['code']

    return app