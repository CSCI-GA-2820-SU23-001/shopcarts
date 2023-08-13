$(function () {

    function update_form_shopcart(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_name").val(res.name);
    }

    function clear_form_shopcart() {
        $("#shopcart_id").val("");
        $("#shopcart_name").val("");
    }

    function update_form_item(res) {
        $("#item_id").val(res.id);
        $("#item_shopcart_id").val(res.shopcart_id);
        $("#item_name").val(res.name);
        $("#item_quantity").val(res.quantity);
        $("#item_price").val(res.price);
    }

    function clear_form_item() {
        $("#item_id").val("");
        $("#item_shopcart_id").val("");
        $("#item_name").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
    }

    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-shopcart-btn").click(function () {

        let name = $("#shopcart_name").val();

        let data = {
            "name": name
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_shopcart(res)
            flash_message("Shopcart created!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-shopcart-btn").click(function() {

        let id = $("#shopcart_id").val();
        let name = $("#shopcart_name").val();

        let data = {
            "name": name
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_shopcart(res)
            flash_message("Shopcart updated!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-shopcart-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_shopcart(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_shopcart()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-shopcart-btn").click(function () {

        let id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_shopcart()
            flash_message("Shopcart deleted!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    $("#reset-shopcart-form-btn").click(function () {
        $("#shopcart_id").val("");
        $("#flash_message").empty();
        clear_form_shopcart()
    });

    // ****************************************
    // Clear a Shopcart
    // ****************************************

    $("#clear-shopcart-btn").click(function () {

        let id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax_list = $.ajax({
            type: "PUT",
            url: `/shopcarts/${id}/clear`,
            contentType: "application/json",
            data: ''
        })

        ajax_list.done(function(res){
            clear_form_shopcart()
            flash_message("Shopcart items cleared!")
        });

        ajax_list.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    $("#search-shopcart-btn").click(function () {

        let name = $("#shopcart_name").val();

        let queryString = ""
        if (name) {
            queryString += 'name=' + name
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_shopcarts_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-3">Name</th>'
            table += '<th class="col-md-1">Item_ID</th>'
            table += '<th class="col-md-3">Item_Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '</tr></thead><tbody>'
            let firstShopcart = "";
            for (let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                items = shopcart['items'];
                if (items.length != 0) {
                    for (let j = 0; j < items.length; j++) {
                        table += `<tr id="row_${i}"><td>${shopcart.id}</td><td>${shopcart.name}</td><td>${shopcart.items[j]['id']}</td><td>${shopcart.items[j]['name']}</td><td>${shopcart.items[j]['quantity']}</td><td>${shopcart.items[j]['price']}</td></tr>`
                    }
                } else {
                    table += `<tr id="row_${i}"><td>${shopcart.id}</td><td>${shopcart.name}</td><td></td><td></td><td></td><td></td></tr>`
                }
                
                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#search_shopcarts_results").append(table);

            if (firstShopcart != "") {
                update_form_shopcart(firstShopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    $("#reset-item-form-btn").click(function () {
        $("#item_id").val("");
        // $("#item_shopcart_id").val("");
        $("#item_name").val("");
        $("#item_quantity").val("");
        $("#item_price").val("");
        $("#flash_message").empty();
        clear_form_shopcart()
    });

    // ****************************************
    // Create an Item under a Shopcart
    // ****************************************

    $("#create-item-btn").click(function () {

        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        // let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "shopcart_id": shopcart_id,
            "name": name,
            "quantity": 1,
            "price": price
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_item(res)
            flash_message("Shopcart item created!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Item under a Shopcart
    // ****************************************

    $("#retrieve-item-btn").click(function () {

        let shopcart_id = $("#item_shopcart_id").val();
        let item_id = $("#item_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_items_results").empty();

            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Shopcart_ID</th>'
            table += '<th class="col-md-4">Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '</tr></thead><tbody>'

            table += `<tr id="row_0"><td>${res.id}</td><td>${res.shopcart_id}</td><td>${res.name}</td><td>${res.quantity}</td><td>${res.price}</td></tr>`;
            table += '</tbody></table>';
            $("#search_items_results").append(table);
            update_form_item(res)

            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_item()
            flash_message(res.responseJSON.message)
        });

    });

    $("#list-item-btn").click(function () {

        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_items_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Shopcart_ID</th>'
            table += '<th class="col-md-4">Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}"><td>${item.id}</td><td>${item.shopcart_id}</td><td>${item.name}</td><td>${item.quantity}</td><td>${item.price}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#search_items_results").append(table);

            if (firstItem != "") {
                update_form_item(firstItem)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item under a Shopcart
    // ****************************************
    $("#delete-item-btn").click(function () {
        let shopcart_id = $("#item_shopcart_id").val();
        let item_id = $("#item_id").val();
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        });
    
        ajax.done(function (res) {
            // clear_form_item();
            
            $("#item_id").val("");
            // $("#item_shopcart_id").val("");
            $("#item_name").val("");
            $("#item_quantity").val("");
            $("#item_price").val("");
            $("#flash_message").empty();
            
            
            flash_message("Item deleted from shopcart!");
        });
    
        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });
    
    });

    $("#update-item-btn").click(function () {

        let item_id = $("#item_id").val();
        let shopcart_id = $("#item_shopcart_id").val();
        let name = $("#item_name").val();
        let quantity = $("#item_quantity").val();
        let price = $("#item_price").val();

        let data = {
            "shopcart_id": shopcart_id,
            "name": name,
            "quantity": parseInt(quantity),
            "price": parseFloat(price)
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });

        ajax.done(function(res){
            update_form_item(res)
            flash_message("Shopcart item updated!")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
