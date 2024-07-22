from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserChat, ChatSession, Document
import pickle
from keras.models import load_model
from django.conf import settings
import os
import random
import numpy as np

model = load_model("media/models/chatbot_model.h5")

with open("media/models/vectorizer.pkl", "rb") as file:
    vectorizer = pickle.load(file)

with open("media/models/label_encoder.pkl", "rb") as file:
    label_encoder = pickle.load(file)

with open("media/models/tag_responses.pkl", "rb") as file:
    tag_responses = pickle.load(file)


def chatbot_response(user_input):
    user_input_vectorized = vectorizer.transform([user_input]).toarray()
    predicted_tag = label_encoder.inverse_transform(
        [np.argmax(model.predict(user_input_vectorized))]
    )[0]
    response = random.choice(tag_responses[predicted_tag])
    print(response)
    return response


# Create your views here.
@login_required
def userhome(request):
    user = request.user
    return render(request, "user/userhomepage.html", {"user": user})


@login_required
def updateprofile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        user = request.user

        if username:
            user.username = username
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email

        user.save()
        return redirect("userhome")
    else:
        return redirect("userhome")


def userchat(request):
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
    session_id = request.GET.get("session_id")
    chats = []

    if session_id:
        session = get_object_or_404(ChatSession, id=session_id, user=user)
        chats = UserChat.objects.filter(session=session).order_by("timestamp")

    context = {
        "sessions": sessions,
        "chats": chats,
        "session_id": session_id,
        "username": user.username,
        "email": user.email,
    }
    return render(request, "user/userchat.html", context)


@login_required
def userchat_action(request, session_id=None):
    user = request.user

    keyword_documents = {
        "house agreement": {
            "file": "Agreements\Basic-Rental-Agreement-Template-Signaturely.pdf",
            "description": 'This Basic Rental Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [LANDLORD NAME] ("Landlord") and [TENANT NAME] ("Tenant").',
        },
        "month rental": {
            "file": "Agreements\Month-To-Month-Rental-Agreement-Template-Signaturely.pdf",
            "description": "A  Month-To-Month Rental Agreement is a type of rental agreement that allows a tenant to rent a property from a landlord on a month-to-month basis. This type of agreement is often used for short-term rentals or when the tenant is unsure of their long-term plans.",
        },
        "marketing": {
            "file": "Agreements\Marketing-Agreement-Template-Signaturely.pdf",
            "description": 'This Marketing Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [MARKETING AGENCY NAME] ("Agency") and [CLIENT NAME] ("Client").',
        },
        "marketing proposal": {
            "file": "Agreements\Marketing-Proposal-Template.pdf",
            "description": "Entering the world of marketing proposals can be a complex endeavor. Luckily, you can craft a successful bid with a suitable template to land you new clients. This guide aims to help you unlock the secrets of practical marketing proposals, all streamlined with an easy-to-use free marketing proposal template.",
        },
        "service": {
            "file": "Agreements\Service-Contract-Template-Signaturely.pdf",
            "description": 'This Service Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [SERVICE PROVIDER NAME] ("Service Provider") and [CLIENT NAME] ("Client").',
        },
        "service proposal": {
            "file": "Agreements\Service-Proposal-Template.pdf",
            "description": "We are pleased to submit this service proposal to [Client Company] for the provision of [Service Name] services. Our team of experts has carefully reviewed your requirements and has developed a customized solution to meet your needs.",
        },
        "accounting": {
            "file": "Agreements\Accounting-Contract-Template-Signaturely.pdf",
            "description": 'An Accounting Contract is a legally binding agreement between a client (the "Client") and an accountant or accounting firm (the "Accountant") that outlines the terms and conditions of the accounting services to be provided. The contract ensures that both parties understand their roles, responsibilities, and expectations.',
        },
        "agency": {
            "file": "Agreements\Agency-Agreement-Template-Signaturely.pdf",
            "description": 'An Agency Template is a document that outlines the terms and conditions of an agency relationship between a principal (the "Principal") and an agent (the "Agent"). The template ensures that both parties understand their roles, responsibilities, and expectations.',
        },
        "bookkeeping": {
            "file": "Agreements\Bookkeeping-Contract-Agreement-Template-Signaturely.pdf",
            "description": 'This Book-Keeping Contract (""Agreement"") is made and entered into on [DATE] (""Effective Date"") by and between [YOUR COMPANY NAME] (""Bookkeeper"") and [CLIENT NAME] (""Client"").',
        },
        "brandambassador contract": {
            "file": "Agreements\Brand-Ambassador-Contract.pdf",
            "description": "Brand ambassador partnerships necessitate structure for thriving longevity. Ambitious collaborations demand formally aligned expectations, while creative spontaneity requires room for evolving. Signaturely’s brand ambassador contract template helps craft timely contracts, conveying clarity, flexibility, and commitment in equal measure.",
        },
        "budget proposal agreement": {
            "file": "Agreements\Budget-Proposal-Template.pdf",
            "description": "Taking control of project finances starts with a solid budget proposal. Signaturely’s free budget proposal template can guide you through the process, ensuring your project gets off the ground with a robust financial framework.",
        },
        "bussiness parternship": {
            "file": "Agreements\Business-Partnership-Agreement.pdf",
            "description": "Navigating the modern business world is like setting sail in unpredictable waters; having a reliable compass can be a game-changer.A business partnership agreement is that compass. It provides structure and security for all parties involved, allowing you to focus on what truly matters: the success of your business.",
        },
        "vechicle lease agreement": {
            "file": "Agreements\Car-Lease-Agreement-Template.pdf",
            "description": "When buying or selling a vehicle, it is crucial to have a comprehensive and legally binding purchase agreement in place. An agreement ensures the protection of both parties involved and facilitates a seamless transfer of ownership.This free vehicle purchase agreement template simplifies the process of a car purchase or sale. This document includes all necessary information about the buyer and seller and specifics about the purchase while ensuring everyone’s rights are upheld according to the law.",
        },
        "vehicle rental agreement": {
            "file": "Agreements\Car-Rental-Agreement.pdf",
            "description": "When buying or selling a vehicle, it is crucial to have a comprehensive and legally binding purchase agreement in place. An agreement ensures the protection of both parties involved and facilitates a seamless transfer of ownership.This free vehicle purchase agreement template simplifies the process of a car purchase or sale. This document includes all necessary information about the buyer and seller and specifics about the purchase while ensuring everyone’s rights are upheld according to the law.",
        },
        "catering contract": {
            "file": "Agreements\Catering-Contract-Agreement-Template-Signaturely.pdf",
            "description": "A Catering Proposal is a document that outlines the services and menu options offered by a catering company to a potential client. The proposal should provide a clear and concise overview of the catering company's capabilities, menu options, and pricing.",
        },
        "coaching agreement": {
            "file": "Agreements\Coaching-Agreement-Template-Signaturely.pdf",
            "description": 'This Coaching Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [COACH NAME] ("Coach") and [CLIENT NAME] ("Client").',
        },
        "cleaning proposal": {
            "file": "Agreements\Cleaning-Proposal-Template.pdf",
            "description": "We are pleased to submit this cleaning proposal to [Client Company] for the provision of cleaning services. Our team of experienced cleaning professionals has carefully reviewed your requirements and has developed a customized cleaning plan to meet your needs",
        },
        "consignment agreement": {
            "file": "Agreements\Consignment-Agreement-Template.pdf",
            "description": "A consignment agreement clearly defines the terms between a consignor and consignee regarding the sale of goods. It’s an essential document for both parties, and having a robust consignment agreement template is critical to moving through your operations efficiently.",
        },
        "construction contract": {
            "file": "Agreements\Construction-Contract-Template-Signaturely.pdf",
            "description": 'A Construction Contract Agreement is a legally binding agreement between a contractor (the "Contractor") and a property owner or developer (the "Owner") that outlines the terms and conditions of a construction project. The contract ensures that both parties understand their roles, responsibilities, and expectations.',
        },
        "consulting agreement": {
            "file": "Agreements\Consulting-Agreement-Template-Signaturely.pdf",
            "description": 'A Consulting Agreement is a contract between a consultant (the "Consultant") and a client (the "Client") that outlines the terms and conditions of the consulting services to be provided. The agreement ensures that both parties understand their roles, responsibilities, and expectations',
        },
        "custody agreement": {
            "file": "Agreements\Custody-Agreement-Template.pdf",
            "description": 'This Custody Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [PARENT 1 NAME] ("Parent 1") and [PARENT 2 NAME] ("Parent 2") regarding the custody of their minor child(ren), CHILD(REN) NAME ("Child(ren)").',
        },
        "distribution agreement": {
            "file": "Agreements\Distribution-Agreement-Template.pdf",
            "description": "A distribution agreement outlines the terms under which a manufacturer grants a distributor the right to distribute, resell, and promote their products in a defined territory. This guide outlines best practices in creating a distribution agreement, and provides a template to kickstart your efforts.",
        },
        "divorce settlement agreement": {
            "file": "Agreements\Divorce-Settlement-Agreement-Template.pdf",
            "description": "Embarking on the divorce process can be a challenging and emotionally charged journey. One critical document that can facilitate this process is a divorce settlement agreement.                                    This guide aims to equip you with an understanding of its relevance and practical insights into crafting one that fits your circumstances.",
        },
        "dj contract": {
            "file": "Agreements\DJ-Contract-Template.pdf",
            "description": 'This agreement is made and entered into on [DATE] ("Effective Date") by and between [DJ NAME] ("DJ") and [CLIENT NAME] ("Client") for the provision of DJ services at [EVENT NAME] ("Event").',
        },
        "employment contract agreement": {
            "file": "Agreements\Employment-Contract-Agreement-Template-Signaturely.pdf",
            "description": 'An Employment Contract is a legally binding agreement between an employer (the "Employer") and an employee (the "Employee") that outlines the terms and conditions of the employment relationship. The contract ensures that both parties understand their roles, responsibilities, and expectations.',
        },
        "equipment rental agreement": {
            "file": "Agreements\Equipment-Rental-Agreement-Template.pdf",
            "description": "Finding the right equipment for your business is a significant achievement. After all, it can act as the backbone of your business value proposition. However, how do you ensure the equipment leasing process is seamless?Welcome to the comprehensive guide to an equipment rental agreement. This article explores its nuances, types, and best practices for drafting a foolproof equipment lease agreement.",
        },
        "event planning contract": {
            "file": "Agreements\Event-Planning-Contract-Template-Signaturely.pdf",
            "description": 'This Event-Planning Contract ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [CLIENT NAME] ("Client") and [EVENT PLANNER NAME] ("Event Planner").',
        },
        "eviction notice": {
            "file": "Agreements\Eviction-Notice-Template.pdf",
            "description": "The premises referred to in this Agreement are located at [Tenant's Address] Premises.The Landlord has served the Tenant with an eviction notice dated [Date of Eviction Notice] Eviction Notice due to [Reason for Eviction, such as non-payment of rent or violation of lease agreement].",
        },
        "freelance contract": {
            "file": "Agreements\Freelance-Contract-Template.pdf",
            "description": 'This Freelance Contract ("Contract") is made and entered into on [DATE] ("Effective Date") by and between [CLIENT NAME] ("Client") and [FREELANCER NAME] ("Freelancer") for the provision of freelance services.',
        },
        "graphic design contract": {
            "file": "Agreements\Graphic-Design-Contract-Template-Signaturely.pdf",
            "description": "Here is a sample Graphic Design Contract: GRAPHIC DESIGN CONTRACTThis Graphic Design Contract ("
            "Contract"
            ") is made and entered into on [DATE] ("
            "Effective Date"
            ") by and between [YOUR COMPANY NAME] ("
            "Designer"
            ") and [CLIENT NAME] ("
            "Client"
            ").1. PROJECT OVERVIEW The Designer agrees to provide graphic design services to the Client, as described in the attached Project Scope document.",
        },
        "home repair contract": {
            "file": "Agreements\Home-Repair-Contract-Template.pdf",
            "description": "Are you embarking on a home repair project? A well-crafted contract can be your safety net, ensuring a smooth operation and protecting both parties involved. This guide will help you navigate the essential elements of a home repair contract, focusing on clarity, legality, and ease.",
        },
        "independent contractor agreement": {
            "file": "Agreements\Independent-Contractor-Agreement-Template-Signaturely.pdf",
            "description": 'This Independent Contractor Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [CLIENT NAME] ("Client") and [CONTRACTOR NAME] ("Contractor").',
        },
        "intellectual property agreement": {
            "file": "Agreements\Intellectual-Property-Agreement-Template-Signaturely.pdf",
            "description": "Intellectual Property (IP) refers to the legal rights that protect creations of the mind, such as inventions, literary and artistic works, and symbols, names, and logos used in commerce. IP laws grant creators exclusive rights to their creations, allowing them to control how their work is used and to benefit from their innovations",
        },
        "interior design contract": {
            "file": "Agreements\Interior-Design-Contract-Template.pdf",
            "description": "Decorating a space is an art form that requires expertise. Ensuring your artistic visions translate into legal assurances can be tricky. Let’s dive into the world of interior design contracts to understand how they create a reliable, legally binding framework for your interior design business needs.",
        },
        "internship contract agreement": {
            "file": "Agreements\Internship-Contract-Agreement-Signaturely.pdf",
            "description": 'This Internship Contract ("Contract") is made and entered into on [DATE] ("Effective Date") by and between [COMPANY NAME] ("Company") and [INTERN NAME] ("Intern").',
        },
        "investment proposal": {
            "file": "Agreements\Investment-Proposal-Template.pdf",
            "description": "An effective investment proposal is critical to seeking financial backing to ignite a new venture or inject life into an existing one. This detailed guide and our free investment proposal template can serve as your roadmap to crafting an attention-grabbing pitch that potential investors find irresistible.",
        },
        "lawn service": {
            "file": "Agreements\Lawn-Service-and-Landscaping-Contract-Template-Signaturely.pdf",
            "description": 'This Lawn Service and Landscaping Contract ("Contract") is made and entered into on [DATE] ("Effective Date") by and between [LAWN SERVICE COMPANY NAME] ("Contractor") and [HOMEOWNER NAME] ("Homeowner").',
        },
        "landscaping": {
            "file": "Agreements\Lawn-Service-and-Landscaping-Contract-Template-Signaturely.pdf",
            "description": 'This Lawn Service and Landscaping Contract ("Contract") is made and entered into on [DATE] ("Effective Date") by and between [LAWN SERVICE COMPANY NAME] ("Contractor") and [HOMEOWNER NAME] ("Homeowner").',
        },
        "license": {
            "file": "Agreements\Licensing-Agreement-Template.pdf",
            "description": "Are you entering the complex realm of  intellectual property and licensing? While it can seem like an uphill battle, there are resources you can take advantage of to come out on top. Arm yourself with Signaturely’s easily accessible and user-friendly licensing agreement templates. Simplify the process, protect your interests, and grant licenses professionally. This article provides an overview of the ins and outs of licensing agreements.",
        },
        "loan": {
            "file": "Agreements\Loan-Agreement-Template-Signaturely.pdf",
            "description": 'A Loan Agreement is a contract between a lender (the "Lender") and a borrower (the "Borrower") that outlines the terms and conditions of a loan. The agreement specifies the amount borrowed, interest rate, repayment schedule, and other essential details to ensure a clear understanding of the loan obligations.',
        },
        "memorandum": {
            "file": "Agreements\Memorandum-Of-Understanding-Template.pdf",
            "description": "A memorandum of understanding (MOU) is an important document to set expectations between two or more parties working together on a project or business deal.",
        },
        "nanny": {
            "file": r"Agreements\Nanny-Contract-Template.pdf",
            "description": "A nanny contract establishes clear caregiving expectations between families and child care providers. Outlining duties, hours, pay rate, time-off, and policies upfront ensures all parties understand the arrangement before commencements. This prevents confusion down the road if questions arise. Make sure to detail issues like taxes, mileage reimbursement, resignation terms, and other specifics relevant to your situation. While adaptations occur as children grow, a signed nanny agreement protects both interests when thoughtfully customized.",
        },
        "nondisclosure": {
            "file": r"Agreements\Non-Disclosure-Agreement-Template-Signaturely.pdf",
            "description": 'This Non-Disclosure Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [DISCLOSING PARTY NAME] ("Disclosing Party") and [RECEIVING PARTY NAME] ("Receiving Party").',
        },
        "onepagelease": {
            "file": "Agreements\One-Page-Lease-Agreement-Template-Signaturely.pdf",
            "description": 'This One Page Lease Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [LANDLORD NAME] ("Landlord") and [TENANT NAME] ("Tenant").',
        },
        "operating": {
            "file": "Agreements\Operating-Agreement-Template.pdf",
            "description": "An Operating Agreement is a legal document that outlines the ownership, management, and operational structure of a Limited Liability Company (LLC). It is a crucial document that helps establish the rules and guidelines for the company's operations, and it is often required by law.",
        },
        "painting": {
            "file": "Agreements\Painting-Contract-Template.pdf",
            "description": "A painting contract formally outlines the agreement between a client and painter, establishing details like scope, timeline, materials, and payment to set clear expectations.",
        },
        "payment": {
            "file": "Agreements\Payment-Agreement-Template-Signaturely.pdf",
            "description": 'A Payment Agreement is a contract between a creditor (the "Creditor") and a debtor (the "Debtor") that outlines the terms and conditions of a debt repayment plan. The agreement specifies the amount of debt, payment schedule, and other essential details to ensure a clear understanding of the payment process and expectations.',
        },
        "training": {
            "file": "Agreements\Personal-Training-Contract-Template-Signaturely.pdf",
            "description": 'A Personal Training Contract is a binding agreement between a personal trainer (the "Trainer") and a client (the "Client") that outlines the terms and conditions of the personal training services to be provided. The contract specifies the scope of work, payment terms, and other essential details to ensure a clear understanding of the personal training process and expectations.',
        },
        "profit": {
            "file": "Agreements\Profit-Sharing-Agreement.pdf",
            "description": "A Profit Sharing Agreement is a contractual arrangement between an employer and employees that outlines the terms and conditions of sharing profits with employees. The agreement specifies how profits will be distributed, the percentage of profits to be shared, and the eligibility criteria for participation.",
        },
        "property": {
            "file": "Agreements\Property-Management-Agreement-Template-Signaturely.pdf",
            "description": 'A Property Management Agreement is a contract between a property owner (the "Owner") and a property management company (the "Manager") that outlines the terms and conditions of the property management services to be provided. The agreement specifies the scope of work, payment terms, and other essential details to ensure a clear understanding of the property management process and expectations.',
        },
        "remodeling": {
            "file": "Agreements\Remodeling-Contract-Template-Signaturely.pdf",
            "description": 'This Remodeling Contract ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [CONTRACTOR NAME] ("Contractor") and [HOMEOWNER NAME] ("Homeowner").',
        },
        "retainer": {
            "file": "Agreements\Retainer-Agreement-Template-Signaturely.pdf",
            "description": "RETAINER AGREEMENT This Retainer Agreement ("
            "Agreement"
            ") is made and entered into on [DATE] ("
            "Effective Date"
            ") by and between [YOUR COMPANY NAME] ("
            "Service Provider"
            ") and [CLIENT NAME] ("
            "Client"
            ").",
        },
        "sales": {
            "file": "Agreements\Sales-Contract-Template-Signaturely.pdf",
            "description": 'This Sales Contract ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [SELLER NAME] ("Seller") and [BUYER NAME] ("Buyer").',
        },
        "shareholder": {
            "file": "Agreements\Shareholders-Agreement-Template.pdf",
            "description": "Running a business is not just about driving sales but also about managing relationships, especially among shareholders. A shareholder agreement serves as an essential tool in navigating this complex business landscape. This article highlights why you need one and how to create one using this free shareholder agreement guide.",
        },
        "seo": {
            "file": "Agreements\Signaturely-SEO-Proposal-Template.pdf",
            "description": "An SEO Proposal Agreement is a contract between a search engine optimization (SEO) service provider and a client that outlines the terms and conditions of the SEO services to be provided. The agreement specifies the scope of work, deliverables, timelines, and payment terms, ensuring a clear understanding of the project's objectives and expectations.",
        },
        "storage": {
            "file": "Agreements\Simple-Storage-Rental-Agreement.pdf",
            "description": "A simple storage rental agreement outlines the relationship between a storage facility owner and an individual renting space to store personal belongings.",
        },
        "website": {
            "file": "Agreements\Simple-Website-Design-Agreement-Template-Signaturely.pdf",
            "description": 'This Simple Website Design Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [YOUR COMPANY NAME] ("Designer") and [CLIENT NAME] ("Client").',
        },
        "socialmedia": {
            "file": "Agreements\Social-Media-Management-Contract.pdf",
            "description": "An effective social media management contract clarifies expectations and protections for clients (typically social media managers) and contractors engaging in a business relationship involving creative digital services.",
        },
        "sponsorship": {
            "file": "Agreements\Sponsorship-Proposal-Template.pdf",
            "description": "We are seeking sponsorship for our [event/project name], which will take place on [date] at [location]. This [event/project] aims to [briefly describe the purpose and objectives of the event/project]. We expect to attract [number] attendees from [target audience] and provide a unique opportunity for [Sponsor's Company] to reach a highly engaged and targeted audience.",
        },
        "subcontractor": {
            "file": "Agreements\Subcontractor-Agreement-Template-Signaturely.pdf",
            "description": 'This Subcontractor Agreement ("Agreement") is made and entered into on [DATE] ("Effective Date") by and between [CONTRACTOR NAME] ("Contractor") and [SUBCONTRACTOR NAME] ("Subcontractor").',
        },
        "sublease": {
            "file": "Agreements\Sublease-Agreement-Template-Signaturely.pdf",
            "description": "This Sub-lease Agreement Agreement is made and entered into on [DATE] Effective Date by and between [SUB-LESSOR'S NAME] Sub-lessor and [SUB-LESSEE'S NAME] Sub-lessee.",
        },
        "termination": {
            "file": "Agreements\Termination-Letter-Template.pdf",
            "description": "We’ve worked with legal experts and proofreaders to create a free termination letter template. It’ll ensure that you handle a dismissal or layoff with the correct legal document.",
        },
        "vehicle purchase": {
            "file": "Agreements\Vehicle-Purchase-Agreement-Template.pdf",
            "description": "When buying or selling a vehicle, it is crucial to have a comprehensive and legally binding purchase agreement in place. An agreement ensures the protection of both parties involved and facilitates a seamless transfer of ownership. This free vehicle purchase agreement template simplifies the process of a car purchase or sale. This document includes all necessary information about the buyer and seller and specifics about the purchase while ensuring everyone’s rights are upheld according to the law.",
        },
        "vendor": {
            "file": "Agreements\Vendor-Contract-Template.pdf",
            "description": "If you’re a business owner looking to save time on vendor sourcing, it’s crucial to have a clear set of standards and expectations for your vendors.An effective way to streamline this process is by using a vendor contract template as an agreement between you and your service provider. This ensures that each party knows their obligations when they enter the agreement. With a well-drafted contract in place, misunderstandings and disputes can be easily avoided in the future.Whether you’re looking for wedding services, catering, or event planning, having a customizable solution can significantly impact your vendor workflow. To help simplify the process for busy business owners, Signaturely offers a free vendor contract template that covers all the essential terms needed to form a legally binding agreement with your vendors.",
        },
        "video production": {
            "file": "Agreements\Video-Production-Proposal-Template-Signaturely.pdf",
            "description": "VIDEO PRODUCTION PROPOSAL CONTRACT This Video production Proposal Contract ("
            "Agreement"
            ") is made and entered into on [DATE] ("
            "Effective Date"
            ") by and between [YOUR COMPANY NAME] ("
            "Producer"
            ") and [CLIENT NAME] ("
            "Client"
            ").1. PROJECT OVERVIEWThe Producer agrees to produce a video project (the "
            "Project"
            ") for the Client, as described in the attached proposal (the "
            "Proposal"
            ").",
        },
        "wedding photography": {
            "file": "Agreements\Wedding-Photography-Contract-Template.pdf",
            "description": 'A Wedding Planner Contract is a binding agreement between a wedding planner and a couple (the "Clients") that outlines the terms and conditions of the wedding planning services to be provided. The contract specifies the scope of work, payment terms, and other essential details to ensure a clear understanding of the wedding planning process and expectations.',
        },
        "wedding planner": {
            "file": "Agreements\Wedding-Planner-Contract-Template-Signaturely.pdf",
            "description": 'A Wedding Planner Contract is a binding agreement between a wedding planner and a couple (the "Clients") that outlines the terms and conditions of the wedding planning services to be provided. The contract specifies the scope of work, payment terms, and other essential details to ensure a clear understanding of the wedding planning process and expectations.',
        },
        "work for hire": {
            "file": "Agreements\Work-For-Hire-Agreement-Template-Signaturely.pdf",
            "description": "A Work For Hire Agreement is a contract between a client and a freelancer or independent contractor that outlines the terms and conditions of a specific project or assignment. The agreement specifies the scope of work, payment terms, intellectual property rights, and other essential details to ensure a clear understanding of the project's objectives and expectations.",
        },
    }

    if request.method == "POST":
        user_input = request.POST.get("user_input").lower().strip()
        if not user_input:
            return redirect("userchat_action", session_id=session_id)

        document_to_send = None
        description = ""
        for keywords, doc_info in keyword_documents.items():
            if all(keyword in user_input for keyword in keywords.split()):
                document_to_send = doc_info["file"]
                description = doc_info["description"]
                break

        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
        else:
            session = ChatSession.objects.create(user=user)

        bot_response = chatbot_response(user_input) if not document_to_send else ""
        chat_entry = UserChat.objects.create(
            session=session, user_input=user_input, result=bot_response
        )

        if document_to_send:
            document_path = os.path.join(settings.MEDIA_ROOT, document_to_send)
            print(f"Checking for document at: {document_path}")  # Debugging line
            if os.path.exists(document_path):
                print(f"Document found: {document_path}")  # Debugging line
                bot_response = f"Please see the attached document for more information: <a href='{settings.MEDIA_URL}{document_to_send}'>{os.path.basename(document_to_send)}</a><br>Description: {description}"
                Document.objects.create(chat=chat_entry, file=document_to_send)
            else:
                print("Document not found.")  # Debugging line
                bot_response = "Sorry, the document could not be found."

            chat_entry.result = bot_response
            chat_entry.save()

        chats = UserChat.objects.filter(session=session).order_by("timestamp")
        context = {
            "user_message": user_input,
            "results": [bot_response],
            "session_id": session.id,
            "chats": chats,
            "sessions": ChatSession.objects.filter(user=user).order_by("-created_at"),
        }
        return render(request, "user/userchat.html", context)
    else:
        sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
            chats = UserChat.objects.filter(session=session).order_by("timestamp")
        else:
            chats = []

        context = {"sessions": sessions, "chats": chats, "session_id": session_id}

        return render(request, "user/userchat.html", context)


@login_required
def delete_chat_session(request, session_id):
    user = request.user
    session = get_object_or_404(ChatSession, id=session_id, user=user)

    if request.method == "POST":
        chats = UserChat.objects.filter(session=session)
        for chat in chats:
            documents = chat.documents.all()
            for document in documents:
                file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
                if os.path.exists(file_path):
                    os.remove(file_path)
        session.delete()
        return redirect("userchat")

    context = {"session": session}
    return render(request, "user/userchat.html", context)


def previous_chats(request):
    user = request.user
    sessions = ChatSession.objects.filter(user=user).order_by("-created_at")
    context = {"sessions": sessions, "username": user.username, "email": user.email}
    return render(request, "user/previous_chats.html", context)


def chat_details(request, session_id):
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    chats = UserChat.objects.filter(session=session).order_by("timestamp")
    chat_data = [
        {"user_input": chat.user_input, "result": chat.result} for chat in chats
    ]
    return JsonResponse({"chats": chat_data})
