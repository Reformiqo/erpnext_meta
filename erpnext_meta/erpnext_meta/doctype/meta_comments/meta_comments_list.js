
frappe.listview_settings['Meta Comments'] = {
    refresh: function(listview) {
        listview.page.add_inner_button("Fetch Comments", function() {
             frappe.call({
                 method: "erpnext_meta.utils.fetch_comments",
                 args: {},
                 callback: function(r) {
                     if(r.message) {
                         frappe.msgprint("Comments Fetched Successfully");
                         listview.refresh();
                         console.log(r.message);
                     }
                 }
             });
        });;
    },
 };