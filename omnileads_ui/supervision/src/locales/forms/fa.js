export default {
    pause_set: {
        new: {
            name: 'نام مجموعه',
            configured_pauses: 'شکست های پیکربندی شده',
            enter_name: 'نام را وارد کنید'
        }
    },
    pause_setting: {
        enter_time: 'زمان را وارد کنید',
        infinite_time: 'زمان بی نهایت'
    },
    call_disposition: {
        enter_name: 'نام را وارد کنید'
    },
    external_system: {
        enter_name: 'نام را وارد کنید'
    },
    form: {
        enter_name: 'نام را وارد کنید',
        enter_description: 'توضیحات را وارد کنید',
        new_field: 'زمینه جدید',
        options_list: 'گزینه های لیست',
        field: {
            type: {
                text: 'متن',
                date: 'تاریخ',
                list: 'آماده',
                text_box: 'جعبه متن'
            }
        },
        validations: {
            required_name: 'نام مورد نیاز است',
            required_description: 'توضیحات لازم است',
            not_empty_list: 'لیست نمی تواند خالی باشد',
            field_already_in_form: 'فیلد قبلاً در فرم وجود دارد',
            option_already_in_list: 'این گزینه قبلاً در لیست موجود است',
            not_empty_form_field: 'حداقل باید یک فیلد در فرم وجود داشته باشد'
        }
    },
    pause: {
        enter_name: 'نام را وارد کنید',
        edit_pause: 'مکث را ویرایش کنید',
        new_pause: 'مکث جدید'
    },
    inbound_route: {
        enter_name: 'نام را وارد کنید',
        enter_phone: 'DID را وارد کنید',
        enter_caller_id: 'پیشوند شناسه تماس گیرنده را وارد کنید',
        edit_inbound_route: 'مسیر ورودی را ویرایش کنید',
        new_inbound_route: 'مسیر ورودی جدید',
        languages: {
            en: 'انگلیسی',
            es: 'اسپانیایی'
        },
        destination_types: {
            campaign: 'کمپین ورودی',
            validation_date: 'اعتبارسنجی تاریخ/زمان',
            ivr: 'تلفن گویا',
            hangup: 'قطع کن',
            id_client: 'شناسه مشتری',
            custom_dst: 'مقصد سفارشی'
        }
    },
    outbound_route: {
        enter_name: 'نام را وارد کنید',
        enter_ring_time: 'زمان زنگ را وارد کنید',
        enter_dial_option: 'وارد گزینه شماره گیری شوید',
        validations: {
            not_empty_dial_patterns: 'باید حداقل یک الگوی شماره گیری وجود داشته باشد',
            not_empty_trunks: 'باید حداقل یک تنه وجود داشته باشد',
            repeated_route_name: 'مسیر خروجی با آن نام از قبل وجود دارد',
            invalid_route_name: 'نام مسیر نامعتبر است',
            trunk_already_exists: 'تنه از قبل وجود دارد'
        }
    },
    dial_pattern: {
        enter_pattern: 'الگو را وارد کنید'
    }
};
