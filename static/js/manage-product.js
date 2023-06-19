var productModal = $("#productModal");
$(function () {
    // JSON data by API call
    $.get(productListApiUrl, function (response) {
        if (response) {
            var table = '';
            $.each(response, function (index, p) {
                table += '<tr data-id="' + p.product_id + '" data-name="' + p.product + '" data-unit="' + p.unit_id + '" data-price="' + p.price_per_unit + '">' +
                    '<td>' + p.product + '</td>' +
                    '<td>' + p.unit_name + '</td>' +
                    '<td>' + p.price_per_unit + '</td>' +
                    '<td><span class="btn btn-xs btn-danger edit-product">Edit</span></td></tr>';
            });
            $("table").find('tbody').empty().html(table);

            // Event listener for edit button
            $(".edit-product").click(function () {
                var row = $(this).closest("tr");
                var name = row.data("name");
                var price = row.data("price");

                // Populate the edit details block
                var editDetails = "<div>Product: <span id='edit-name'>" + name + "</span></div>";
    
                editDetails += "<div>Price Per Unit: <input type='text' id='edit-price' value='" + price + "'></div>";
                $("#edit-details").html(editDetails);

                // Display the modal
                $("#edit-modal").css("display", "block");
            });

            // Event listener for close button in the modal
            $(".close").click(function () {
                $("#edit-modal").css("display", "none");
            });

            // Event listener for save button in the modal
            $("#save-button").click(function () {
                var name = $("#edit-name").text();
                var price = $("#edit-price").val();

                // Send the updated details to Flask API
                $.ajax({
                    url: "/update_product", // Update the URL to match your Flask route
                    type: "POST",
                    data: JSON.stringify({ name: name, price: price }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (response) {
                        console.log("Product details updated successfully");
   
                        var message = $("<div>").addClass("message");
                        message.html("<p>Product updated successfully</p><button id='ok-button'>OK</button>");
                        $("body").append(message);

                        // Event listener for OK button in the message
                        $("#ok-button").click(function () {
                            // Close the message
                            message.remove();
                            // Refresh the page
                            location.reload();
                        });
                    },
                    error: function (xhr, status, error) {
                        // Handle the error response
                        console.error("Error updating product details: " + error);
                    }
                });

                // Close the modal
                $("#edit-modal").css("display", "none");
            });
        }
    });
});


    // Save Product
    $("#saveProduct").on("click", function () {
        // If we found id value in form then update product detail
        var data = $("#productForm").serializeArray();
        var requestPayload = {
            product: null,
            unit_id: null,
            price_per_unit: null
        };
        for (var i=0;i<data.length;++i) {
            var element = data[i];
            switch(element.name) {
                case 'name':
                    requestPayload.product = element.value;
                    break;
                case 'units':
                    requestPayload.unit_id = element.value;
                    break;
                case 'price':
                    requestPayload.price_per_unit = element.value;
                    break;
            }
        }
        callApi("POST", productSaveApiUrl, {
            'data': JSON.stringify(requestPayload)
        });
    });

    $(document).on("click", ".delete-product", function (){
        var tr = $(this).closest('tr');
        var data = {
            product_id : tr.data('id')
        };
        var isDelete = confirm("Are you sure to delete "+ tr.data('name') +" item?");
        if (isDelete) {
            callApi("POST", productDeleteApiUrl, data);
        }
    });

    productModal.on('hide.bs.modal', function(){
        $("#id").val('0');
        $("#name, #unit, #price").val('');
        productModal.find('.modal-title').text('Add New Product');
    });

    productModal.on('show.bs.modal', function(){
        //JSON data by API call
        $.get(uomListApiUrl, function (response) {
            if(response) {
                var options = '<option value="">--Select--</option>';
                $.each(response, function(index, unit) {
                    options += '<option value="'+ unit.unit_id +'">'+ unit.unit_name +'</option>';
                });
                $("#units").empty().html(options);
            }
        });
    });