$(function () {

    function update_form_shopcart(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_name").val(res.name);
    }

    function clear_form_shopcart() {
        $("#shopcart_id").val("");
        $("#shopcart_name").val("");
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
            flash_message("Success")
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
            flash_message("Success")
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
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });

    });

    $("#reset-shopcart-form-btn").click(function () {
        $("#shopcart_id").val("");
        $("#flash_message").empty();
        clear_form_shopcart()
    });

    $("#clear-shopcart-btn").click(function () {

        let name = $("#shopcart_name").val()

        $("#flash_message").empty();

        let ajax_list = $.ajax({
            type: "GET",
            url: `/shopcarts`,
            contentType: "application/json",
            data: ''
        })

        ajax_list.done(function(res){
            for (let i=0; i < res.length; i++) {
                let shopcart = res[i];
                shopcart_id = shopcart.id;
                items = shopcart['items'];
                if (items.length != 0) {
                    for (let j=0; j < items.length; j++) {
                        item_id = shopcart.items[j].id;
                        $.ajax({
                            type: "DELETE",
                            url: `/shopcarts/${shopcart_id}/items/${item_id}`,
                            contentType: "application/json",
                            data: '',
                        })
                    }
                }

            }
        });

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
})