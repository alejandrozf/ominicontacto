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
    external_site: {
        methods: {
            post: 'POST',
            get: 'GET'
        },
        triggers: {
            opt1: 'عامل',
            opt2: 'خودکار',
            opt3: 'سرور',
            opt4: 'صلاحیت'
        },
        objectives: {
            opt1: 'تعبیه شده است',
            opt2: 'برگه جدید'
        },
        formats: {
            opt1: 'multipart/form-data',
            opt2: 'application/x-www-form-urlencoded',
            opt3: 'text/plain',
            opt4: 'application/json'
        }
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
            not_empty_form_field: 'حداقل باید یک فیلد در فرم وجود داشته باشد',
            repeated_form_name: 'قبلاً فرمی با آن نام وجود دارد'
        }
    },
    pause: {
        enter_name: 'نام را وارد کنید',
        edit_pause: 'مکث را ویرایش کنید',
        new_pause: 'مکث جدید',
        validations: {
            repeated_pause_name: 'در حال حاضر یک مکث با این نام وجود دارد'
        },
        types: {
            opt1: 'سازنده',
            opt2: 'تفریحی'
        }
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
        on_row_reorder: 'مسیرهای مرتب شده مجدد، برای نهایی کردن تغییر، اقدام ترتیب مجدد را اجرا کنید',
        validations: {
            not_empty_dial_patterns: 'باید حداقل یک الگوی شماره گیری وجود داشته باشد',
            not_empty_trunks: 'باید حداقل یک تنه وجود داشته باشد',
            repeated_route_name: 'مسیر خروجی با آن نام از قبل وجود دارد',
            invalid_route_name: 'نام مسیر نامعتبر است',
            trunk_already_exists: 'تنه از قبل وجود دارد',
            orphan_trunks: 'با حذف مسیر خروجی، سیپ ترانک های زیر توسط مسیرهای خروجی بلااستفاده می مانند',
            repeated_dial_pattern_prefix: 'قبلاً یک الگوی شماره گیری با آن پیشوند وجود دارد',
            repeated_dial_pattern_rule: 'در حال حاضر یک الگوی شماره گیری با آن قانون وجود دارد'
        }
    },
    dial_pattern: {
        enter_pattern: 'الگو را وارد کنید'
    },
    group_of_hour: {
        enter_name: 'نام را وارد کنید',
        validations: {
            not_empty_time_validations: 'باید حداقل یک بار اعتبارسنجی وجود داشته باشد',
            repeated_group_name: 'در حال حاضر یک گروه زمانی با آن نام وجود دارد',
            time_validation_already_exists: 'اعتبار زمانی از قبل وجود دارد'
        }
    },
    external_site_authentication: {
        placeholders: {
            url: 'مثال: https://www.omnileads.net/',
            name: 'نام را وارد کنید',
            username: 'نام کاربری را وارد کنید',
            campo_token: 'نام فیلد نشانه را وارد کنید',
            campo_duracion: 'نام فیلد را برای مدت زمان وارد کنید',
            duracion: 'مدت زمان را وارد کنید'
        },
        helpers: {
            username: 'بدون فاصله',
            campo_token: 'فیلدی که توکن دسترسی در آن می آید',
            campo_duracion: 'فیلدی که مدت زمان توکن در آن می آید',
            duracion: 'در چند ثانیه'
        },
        validations: {
            name_already_exist: 'نام از قبل وجود دارد',
            invalid_campo_duracion: 'اگر مدت زمان وجود نداشته باشد، قسمت duration باید وجود داشته باشد.',
            invalid_name_campo_token: 'نام فیلد نشانه نامعتبر است',
            invalid_name_campo_duracion: 'نام فیلد مدت نامعتبر است'
        }
    },
    ivr: {
        enter_name: 'نام را وارد کنید',
        enter_description: 'توضیحات را وارد کنید',
        validations: {
            not_empty_time_validations: 'باید حداقل یک بار اعتبارسنجی وجود داشته باشد',
            repeated_ivr_name: 'تلفن گویا با این نام از قبل وجود دارد',
            destination_option_already_exists: 'گزینه مقصد از قبل وجود دارد'
        },
        destination_types: {
            campaign: 'کمپین ورودی',
            validation_date: 'اعتبارسنجی تاریخ/زمان',
            ivr: 'تلفن گویا',
            hangup: 'قطع کن',
            id_client: 'شناسه مشتری',
            custom_dst: 'مقصد سفارشی'
        },
        audios: {
            external: {
                drag_and_drop: 'برای آپلود فایل ها را به اینجا بکشید و رها کنید'
            },
            validations: {
                required_internal_file: 'فایل داخلی مورد نیاز است',
                required_external_file: 'فایل خارجی مورد نیاز است'
            }
        }
    },
    destination_option: {
        validations: {
            repeated_dtmf: 'در حال حاضر یک گزینه مقصد با آن DTMF وجود دارد',
            invalid_dtmf: 'مقدار DTMF باید یک رقم (0-9) یا یک کاراکتر (#، -، *) باشد.'
        }
    },
    register_server: {
        enter_name: 'نام یا شرکت را وارد کنید',
        enter_password: 'رمز عبور را وارد کنید',
        enter_email: 'ایمیل را وارد کنید',
        enter_phone: 'مثال: 5555555555',
        validations: {
            forbidden: 'شما مجوز ثبت نمونه را ندارید. لطفا با مدیر خود تماس بگیرید'
        }
    },
    whatsapp: {
        provider: {
            types: {
                twilio: 'تویلیو',
                meta: 'هدف',
                gupshup: 'GupShup'
            }
        },
        message_template: {
            types: {
                text: 'متن',
                image: 'تصویر',
                file: 'بایگانی',
                audio: 'سمعی',
                video: 'ویدئو',
                sticker: 'برچسب ها',
                location: 'محل',
                contact: 'مخاطب'
            },
            fields: {
                text: 'متن',
                url: 'آدرس های اینترنتی',
                preview_url: 'URL قبلی',
                caption: 'عنوان',
                filename: 'نام فایل',
                longitude: 'طول',
                latitude: 'عرض جغرافیایی',
                name: 'نام',
                address: 'جهت'
            },
            help_text: {
                audio: {
                    url: 'آدرس عمومی فایل صوتی'
                },
                image: {
                    original_url: 'URL عمومی تصویر میزبان',
                    preview_url: 'URL عمومی تصویر کوچک تصویر',
                    caption: 'شرح تصویر'
                },
                file: {
                    url: 'URL عمومی فایل میزبانی شده',
                    filename: 'نام فایل'
                },
                video: {
                    url: 'آدرس عمومی فایل ویدیویی',
                    caption: 'کپشن ویدیو'
                },
                sticker: {
                    url: 'URL عمومی فایل استیکر'
                }
            }
        },
        line: {
            validations: {
                field_is_required: '{field} این لازم است'
            },
            destination_types: {
                campaign: 'زنگ'
            },
            options: {
                success_create: 'گزینه مقصد با موفقیت ایجاد شد',
                success_update: 'گزینه مقصد با موفقیت به روز شد',
                success_delete: 'گزینه مقصد با موفقیت حذف شد',
                empty_options: 'هیچ گزینه مقصد پیکربندی نشده است'
            }
        },
        group_of_message_template: {
            validations: {
                not_empty_templates: 'حداقل باید یک الگو وجود داشته باشد'
            }
        },
        group_of_whatsapp_template: {
            validations: {
                not_empty_templates: 'حداقل باید یک الگو وجود داشته باشد'
            }
        },
        contact: {
            validations: {
                field_is_required: '{field} این لازم است',
                invalid_field: '{field} دارای قالب نامعتبر است'
            }
        },
        disposition_chat: {
            validations: {
                field_is_required: '{field} این لازم است'
            },
            form_types: {
                management: 'مدیریت',
                schedule: 'دفتر خاطرات',
                no_action: 'هیچ اقدامی'
            },
            field_types: {
                text: 'متن',
                date: 'تاریخ',
                list: 'فهرست کنید',
                text_box: 'جعبه متن'
            }
        },
        reports: {
            campaign: {
                conversation: {
                    form_filters: {
                        start_date: 'تاریخ شروع',
                        end_date: 'تاریخ پایان',
                        phone: 'تلفن',
                        agent: 'عامل',
                        placeholders: {
                            start_date: 'تاریخ را انتخاب کنید',
                            end_date: 'تاریخ را انتخاب کنید',
                            phone: 'گوشی را وارد کنید',
                            agent: 'نمایندگان را انتخاب کنید',
                            without_agent: 'هیچ عاملی'
                        }
                    },
                    validatios: {
                        biggest_start_data: 'تاریخ شروع نمی تواند بزرگتر از تاریخ پایان باشد'
                    }
                }
            }
        }
    }
};
