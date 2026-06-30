package medviet.data_access

import future.keywords.if

test_admin_allowed if {
    allow with input as {
        "user": {"role": "admin"},
        "resource": "any",
        "action": "any"
    }
}

test_ml_engineer_allowed if {
    allow with input as {
        "user": {"role": "ml_engineer"},
        "resource": "training_data",
        "action": "read"
    }
    allow with input as {
        "user": {"role": "ml_engineer"},
        "resource": "model_artifacts",
        "action": "write"
    }
}

test_ml_engineer_denied if {
    not allow with input as {
        "user": {"role": "ml_engineer"},
        "resource": "production_data",
        "action": "delete"
    }
}

test_data_analyst_allowed if {
    allow with input as {
        "user": {"role": "data_analyst"},
        "resource": "aggregated_metrics",
        "action": "read"
    }
    allow with input as {
        "user": {"role": "data_analyst"},
        "resource": "reports",
        "action": "write"
    }
}

test_data_analyst_denied if {
    not allow with input as {
        "user": {"role": "data_analyst"},
        "resource": "patient_data",
        "action": "read"
    }
}

test_intern_allowed if {
    allow with input as {
        "user": {"role": "intern"},
        "resource": "sandbox_data",
        "action": "read"
    }
}

test_intern_denied if {
    not allow with input as {
        "user": {"role": "intern"},
        "resource": "production_data",
        "action": "read"
    }
}

test_restricted_data_outside_vn_denied if {
    deny with input as {
        "data_classification": "restricted",
        "destination_country": "US"
    }
}
